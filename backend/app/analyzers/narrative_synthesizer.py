"""Stage 2: Narrative synthesis and idea generation using LLM.

Aggregates signals from the past 14 days and synthesizes them into
narratives with actionable product ideas.
"""

import json
from datetime import timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzers.llm_client import llm_client
from app.models.signal import Signal
from app.models.narrative import Narrative, NarrativeSource
from app.models.idea import Idea
from app.models.scraped_content import ScrapedContent
from app.models.data_source import DataSource
from app.config import get_settings
from app.utils.helpers import utcnow
from app.utils.logger import logger

settings = get_settings()


NARRATIVE_SYNTHESIS_PROMPT = """
You are the core reasoning engine of a Solana Ecosystem Narrative Detection Tool.

Your role is to receive structured signal reports extracted from multiple data
sources over the past 14 days, then identify the most important EMERGING
NARRATIVES within the Solana ecosystem and generate high-quality, actionable
product ideas around each one.

## Who Uses This Output

- Founders deciding what to build next on Solana
- Investors looking for early signals before a category gets crowded
- Ecosystem teams at Solana Foundation, Superteam, and accelerators tracking
  what builders are gravitating toward

## Definition of a Narrative

A narrative is NOT just a trending topic. A narrative is:

- A directional shift in how people are building, using, or thinking about
  Solana
- Backed by signals from multiple independent sources (cross-source validation)
- Early enough that it is not yet widely covered or obvious
- Actionable — something a founder could build a product around right now

## Your Signal Reports

The following JSON array contains signal reports from {total_sources} sources
scraped between {start_date} and {end_date}:

{all_signal_reports}

## Instructions

1. Read all signal reports carefully
2. Look for CONVERGENCE — signals appearing across multiple sources are
   stronger narratives than single-source signals
3. Rank narratives by: cross-source validation > novelty > signal strength
4. For each narrative, generate 3-5 product ideas. Each idea must be:
   - Concrete and specific (not "build a DeFi app")
   - Grounded in the evidence you found — cite which signals support it
   - Evaluated for market potential with honest reasoning
   - Described with a clear problem it solves and why Solana is the right
     platform for it
5. Be skeptical. If signals are weak or only appear in one source, mark the
   narrative confidence as low. Do not inflate weak signals into strong
   narratives to fill space.
6. Prioritize NOVELTY and EXPLAINABILITY over volume. 4 strong narratives
   beats 10 weak ones.

Return ONLY valid JSON. No markdown fences, no preamble, no text outside JSON.

## Output Schema

{{
  "run_date": "{end_date}",
  "fortnight_period": "{start_date} to {end_date}",
  "total_sources_analyzed": {total_sources},
  "narratives": [
    {{
      "rank": 1,
      "title": "Concise narrative title",
      "summary": "3-4 sentence explanation of what is emerging, what changed
                  this fortnight, and why it matters to the Solana ecosystem",
      "confidence": "high | medium | low",
      "confidence_reasoning": "Why you rated confidence this way",
      "supporting_sources": ["source_name_1", "source_name_2"],
      "key_evidence": [
        "Specific quote or data point from source X",
        "Specific observation from source Y"
      ],
      "tags": ["defi", "infrastructure", "consumer", "mobile", "developer-tooling", "hackathon"],
      "product_ideas": [
        {{
          "title": "Product idea name",
          "description": "What this product does in 2-3 sentences",
          "problem": "The specific gap or pain point this solves",
          "solution": "How this product solves it and why now is the right time",
          "why_solana": "Why Solana specifically is the right chain for this",
          "scale_potential": "Why this could grow — TAM, comparable products etc.",
          "market_signals": "Any data points suggesting demand exists",
          "supporting_signals": ["signal_title_1", "signal_title_2"]
        }}
      ]
    }}
  ],
  "total_narratives_found": 0,
  "low_confidence_observations": [
    "Brief note about something potentially interesting but not strong enough"
  ]
}}
"""


async def run_narrative_synthesis(db: AsyncSession) -> dict:
    """
    Run Stage 2 narrative synthesis.

    1. Gather all signals from the past 14 days
    2. Group signals by source
    3. Send to LLM for narrative detection and idea generation
    4. Store narratives and ideas in database
    """
    now = utcnow()
    start_date = now - timedelta(days=settings.NARRATIVE_SYNTHESIS_INTERVAL_DAYS)

    # Fetch signals with their content and source info
    result = await db.execute(
        select(Signal, ScrapedContent, DataSource)
        .join(ScrapedContent, Signal.scraped_content_id == ScrapedContent.id)
        .join(DataSource, ScrapedContent.data_source_id == DataSource.id)
        .where(Signal.created_at >= start_date)
        .order_by(Signal.created_at.desc())
    )
    rows = result.all()

    if not rows:
        logger.info("[STAGE 2] No signals found in past 14 days — skipping synthesis")
        return {"narratives_created": 0, "ideas_created": 0}

    # Build signal reports grouped by source
    source_signals: dict[str, list[dict]] = {}
    source_id_map: dict[str, int] = {}  # source_name -> data_source_id

    for signal, content, ds in rows:
        if ds.name not in source_signals:
            source_signals[ds.name] = []
            source_id_map[ds.name] = ds.id

        source_signals[ds.name].append({
            "signal_title": signal.signal_title,
            "description": signal.description,
            "signal_type": signal.signal_type,
            "novelty": signal.novelty,
            "evidence": signal.evidence,
            "related_projects": signal.related_projects,
            "tags": signal.tags,
            "source_url": content.source_url,
        })

    # Format signal reports for the prompt
    all_reports = []
    for source_name, signals in source_signals.items():
        all_reports.append({
            "source_name": source_name,
            "signal_count": len(signals),
            "signals": signals,
        })

    total_sources = len(source_signals)
    total_signal_count = sum(len(s) for s in source_signals.values())
    logger.info(f"[STAGE 2] Synthesizing narratives from {total_signal_count} signals across {total_sources} sources")
    for src_name, sigs in source_signals.items():
        logger.info(f"[STAGE 2]   {src_name}: {len(sigs)} signals")

    # Build and send prompt
    prompt = NARRATIVE_SYNTHESIS_PROMPT.format(
        total_sources=total_sources,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=now.strftime("%Y-%m-%d"),
        all_signal_reports=json.dumps(all_reports, indent=2, default=str),
    )

    logger.info("[STAGE 2] Sending signals to LLM for narrative synthesis...")
    llm_result = await llm_client.generate_json(prompt)
    if llm_result is None:
        logger.error("[STAGE 2] LLM returned no result for narrative synthesis")
        return {"narratives_created": 0, "ideas_created": 0}

    # Deactivate old narratives that no longer have fresh signals
    await _deactivate_stale_narratives(db)

    # Store new narratives and ideas
    narratives_data = llm_result.get("narratives", [])
    logger.info(f"[STAGE 2] LLM detected {len(narratives_data)} narratives")
    narratives_created = 0
    ideas_created = 0

    for n_data in narratives_data:
        try:
            narrative = Narrative(
                title=n_data.get("title", "Untitled Narrative"),
                summary=n_data.get("summary", ""),
                confidence=n_data.get("confidence", "low"),
                confidence_reasoning=n_data.get("confidence_reasoning", ""),
                is_active=True,
                rank=n_data.get("rank"),
                tags=n_data.get("tags", []),
                key_evidence=n_data.get("key_evidence", []),
                supporting_source_names=n_data.get("supporting_sources", []),
                last_detected_at=now,
            )
            db.add(narrative)
            await db.flush()
            narratives_created += 1
            logger.info(
                f"[STAGE 2]   Narrative #{narratives_created}: \"{narrative.title}\" "
                f"(confidence={narrative.confidence}, tags={narrative.tags})"
            )

            # Create narrative_sources links
            for src_name in n_data.get("supporting_sources", []):
                ds_id = source_id_map.get(src_name)
                if ds_id:
                    # Count signals from this source for this narrative
                    src_signal_count = len(source_signals.get(src_name, []))
                    ns = NarrativeSource(
                        narrative_id=narrative.id,
                        data_source_id=ds_id,
                        signal_count=src_signal_count,
                    )
                    db.add(ns)

            # Create ideas
            idea_list = n_data.get("product_ideas", [])[:5]
            logger.info(f"[STAGE 2]     Generating {len(idea_list)} ideas for this narrative")
            for idea_data in idea_list:
                idea = Idea(
                    narrative_id=narrative.id,
                    title=idea_data.get("title", "Untitled Idea"),
                    description=idea_data.get("description", ""),
                    problem=idea_data.get("problem", ""),
                    solution=idea_data.get("solution", ""),
                    why_solana=idea_data.get("why_solana", ""),
                    scale_potential=idea_data.get("scale_potential", ""),
                    market_signals=idea_data.get("market_signals", ""),
                    supporting_signals=idea_data.get("supporting_signals", []),
                )
                db.add(idea)
                ideas_created += 1

        except Exception as e:
            logger.error(f"Error storing narrative: {e}")

    await db.commit()

    # Calculate velocity scores for new narratives
    await _update_velocity_scores(db)

    summary = {
        "narratives_created": narratives_created,
        "ideas_created": ideas_created,
        "sources_analyzed": total_sources,
        "total_signals": sum(len(s) for s in source_signals.values()),
    }
    logger.info(f"Stage 2 complete: {summary}")
    return summary


async def _deactivate_stale_narratives(db: AsyncSession) -> int:
    """Mark narratives as inactive if no new signals in NARRATIVE_INACTIVE_AFTER_DAYS."""
    cutoff = utcnow() - timedelta(days=settings.NARRATIVE_INACTIVE_AFTER_DAYS)

    result = await db.execute(
        select(Narrative).where(
            Narrative.is_active == True,  # noqa: E712
            Narrative.last_detected_at < cutoff,
        )
    )
    stale = result.scalars().all()

    for n in stale:
        n.is_active = False
        n.updated_at = utcnow()

    if stale:
        logger.info(f"Deactivated {len(stale)} stale narratives")
        await db.flush()

    return len(stale)


async def _update_velocity_scores(db: AsyncSession) -> None:
    """
    Calculate velocity scores for all active narratives.

    velocity_score = signal_count * 0.4 + source_diversity * 0.3 + recency * 0.2 + novelty_avg * 0.1
    """
    result = await db.execute(
        select(Narrative).where(Narrative.is_active == True)  # noqa: E712
    )
    active = result.scalars().all()

    now = utcnow()

    for narrative in active:
        # Signal count from narrative_sources
        ns_result = await db.execute(
            select(func.sum(NarrativeSource.signal_count)).where(
                NarrativeSource.narrative_id == narrative.id
            )
        )
        signal_count = ns_result.scalar() or 0

        # Source diversity (number of distinct sources)
        src_count_result = await db.execute(
            select(func.count(NarrativeSource.id)).where(
                NarrativeSource.narrative_id == narrative.id
            )
        )
        source_diversity = src_count_result.scalar() or 0

        # Recency factor (1.0 if detected today, decays)
        days_since = (now - narrative.last_detected_at).days if narrative.last_detected_at else 14
        recency_factor = max(0.0, 1.0 - (days_since * settings.VELOCITY_DECAY_RATE))

        # Novelty average from confidence
        novelty_map = {"high": 1.0, "medium": 0.6, "low": 0.3}
        novelty_avg = novelty_map.get(narrative.confidence, 0.3)

        velocity = (
            min(signal_count, 50) * 0.4
            + min(source_diversity, 10) * 0.3
            + recency_factor * 0.2
            + novelty_avg * 0.1
        )

        narrative.velocity_score = round(velocity, 3)

    await db.flush()
    await db.commit()
    logger.info(f"Updated velocity scores for {len(active)} active narratives")
