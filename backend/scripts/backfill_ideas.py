"""Backfill product ideas for narratives that have fewer than 3.

Usage (from backend/):
    python3 -m scripts.backfill_ideas            # backfill all under-populated narratives
    python3 -m scripts.backfill_ideas --dry-run   # preview without writing to DB
    python3 -m scripts.backfill_ideas --id 42     # backfill a single narrative by ID
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Ensure the backend package is importable when running as `python3 -m scripts.backfill_ideas`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzers.llm_client import llm_client
from app.analyzers.prompts import get_idea_backfill_prompt
from app.database import async_session_factory
from app.models.narrative import Narrative
from app.models.idea import Idea
from app.utils.logger import logger

MIN_IDEAS = 3
MAX_IDEAS = 5

_SYSTEM_PROMPT = (
    "You are a strict JSON generator. "
    "Return ONLY valid JSON with no markdown/code fences and no extra text. "
    "Do not invent evidence; only use the narrative context provided."
)


def _format_existing_ideas(ideas: list[Idea]) -> str:
    """Serialize existing ideas into a readable block the LLM can reference."""
    if not ideas:
        return "(none — this narrative has no ideas yet)"
    lines: list[str] = []
    for i, idea in enumerate(ideas, 1):
        lines.append(
            f"{i}. **{idea.title}**\n"
            f"   Description: {idea.description}\n"
            f"   Problem: {idea.problem}\n"
            f"   Solution: {idea.solution}"
        )
    return "\n\n".join(lines)


def _format_key_evidence(evidence: list) -> str:
    """Serialize key_evidence JSON into a readable block."""
    if not evidence:
        return "(no structured evidence available)"
    lines: list[str] = []
    for ev in evidence:
        if isinstance(ev, dict):
            source = ev.get("source_name", "Unknown")
            text = ev.get("evidence") or ev.get("quote") or ev.get("observation") or ""
            url = ev.get("content_url") or ""
            sig_title = ev.get("signal_title") or ""
            entry = f"- [{source}]"
            if sig_title:
                entry += f" Signal: {sig_title}"
            if text:
                entry += f"\n  \"{text}\""
            if url:
                entry += f"\n  URL: {url}"
            lines.append(entry)
        else:
            lines.append(f"- {ev}")
    return "\n".join(lines)


async def backfill_narrative(db: AsyncSession, narrative: Narrative, dry_run: bool) -> int:
    """Generate and persist missing ideas for a single narrative. Returns count of new ideas."""
    current_count = len(narrative.ideas)
    if current_count >= MIN_IDEAS:
        return 0

    ideas_needed = MIN_IDEAS - current_count
    target_ideas = MIN_IDEAS

    logger.info(
        f"[BACKFILL] Narrative #{narrative.id} \"{narrative.title}\" — "
        f"has {current_count} idea(s), need {ideas_needed} more"
    )

    prompt_template = get_idea_backfill_prompt()
    prompt = prompt_template.format(
        target_ideas=target_ideas,
        ideas_needed=ideas_needed,
        narrative_title=narrative.title,
        narrative_summary=narrative.summary,
        narrative_confidence=narrative.confidence,
        confidence_reasoning=narrative.confidence_reasoning or "",
        narrative_tags=json.dumps(narrative.tags or []),
        key_evidence=_format_key_evidence(narrative.key_evidence or []),
        existing_ideas=_format_existing_ideas(list(narrative.ideas)),
    )

    if dry_run:
        logger.info(f"[BACKFILL] [DRY RUN] Would send prompt for narrative #{narrative.id}")
        return 0

    llm_result = await llm_client.generate_json(prompt, system_prompt=_SYSTEM_PROMPT)
    if llm_result is None:
        logger.error(f"[BACKFILL] LLM returned no result for narrative #{narrative.id}")
        return 0

    new_ideas_data = llm_result.get("new_product_ideas", [])
    if not new_ideas_data:
        logger.warning(f"[BACKFILL] LLM returned empty ideas list for narrative #{narrative.id}")
        return 0

    # Deduplicate against existing idea titles (case-insensitive)
    existing_titles = {idea.title.lower().strip() for idea in narrative.ideas}
    created = 0

    for idea_data in new_ideas_data:
        title = (idea_data.get("title") or "Untitled Idea").strip()
        if title.lower().strip() in existing_titles:
            logger.info(f"[BACKFILL] Skipping duplicate idea: \"{title}\"")
            continue

        # Don't exceed MAX_IDEAS total
        if current_count + created >= MAX_IDEAS:
            logger.info(f"[BACKFILL] Reached max {MAX_IDEAS} ideas for narrative #{narrative.id}, stopping")
            break

        idea = Idea(
            narrative_id=narrative.id,
            title=title,
            description=idea_data.get("description", ""),
            problem=idea_data.get("problem", ""),
            solution=idea_data.get("solution", ""),
            why_solana=idea_data.get("why_solana", ""),
            scale_potential=idea_data.get("scale_potential", ""),
            market_signals=idea_data.get("market_signals", ""),
            supporting_signals=idea_data.get("supporting_signals", []),
        )
        db.add(idea)
        existing_titles.add(title.lower().strip())
        created += 1
        logger.info(f"[BACKFILL]   + Idea: \"{title}\"")

    if created > 0:
        await db.flush()

    total = current_count + created
    if total < MIN_IDEAS:
        logger.warning(
            f"[BACKFILL] Narrative #{narrative.id} still only has {total} idea(s) "
            f"after backfill (minimum is {MIN_IDEAS})"
        )

    return created


async def main(dry_run: bool = False, narrative_id: int | None = None) -> None:
    """Find all narratives with < 3 ideas and backfill them."""
    async with async_session_factory() as db:
        # Build query for narratives with fewer than MIN_IDEAS ideas
        if narrative_id is not None:
            result = await db.execute(
                select(Narrative).where(Narrative.id == narrative_id)
            )
            narratives = list(result.scalars().all())
            if not narratives:
                logger.error(f"[BACKFILL] Narrative #{narrative_id} not found")
                return
        else:
            # Find narratives with < MIN_IDEAS ideas using a subquery
            idea_count_sq = (
                select(
                    Idea.narrative_id,
                    func.count(Idea.id).label("idea_count"),
                )
                .group_by(Idea.narrative_id)
                .subquery()
            )

            result = await db.execute(
                select(Narrative)
                .outerjoin(idea_count_sq, Narrative.id == idea_count_sq.c.narrative_id)
                .where(
                    Narrative.is_active == True,  # noqa: E712
                    (idea_count_sq.c.idea_count < MIN_IDEAS) | (idea_count_sq.c.idea_count.is_(None)),
                )
                .order_by(Narrative.id)
            )
            narratives = list(result.scalars().all())

        if not narratives:
            logger.info("[BACKFILL] All narratives already have >= 3 ideas. Nothing to do.")
            return

        logger.info(f"[BACKFILL] Found {len(narratives)} narrative(s) needing backfill")
        if dry_run:
            logger.info("[BACKFILL] Running in DRY RUN mode — no changes will be written")

        total_created = 0
        for narrative in narratives:
            try:
                created = await backfill_narrative(db, narrative, dry_run)
                total_created += created
            except Exception as e:
                logger.error(f"[BACKFILL] Error processing narrative #{narrative.id}: {e}")

        if not dry_run:
            await db.commit()

        logger.info(
            f"[BACKFILL] Done. Processed {len(narratives)} narrative(s), "
            f"created {total_created} new idea(s)."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill ideas for narratives with fewer than 3.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to database")
    parser.add_argument("--id", type=int, default=None, dest="narrative_id", help="Backfill a single narrative by ID")
    args = parser.parse_args()

    asyncio.run(main(dry_run=args.dry_run, narrative_id=args.narrative_id))
