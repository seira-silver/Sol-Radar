"""Stage 2: Narrative synthesis and idea generation using LLM.

Aggregates recent signals (configurable lookback window) and synthesizes
them into narratives with actionable product ideas.
"""

import json
from datetime import timedelta

import sqlalchemy as sa
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzers.llm_client import llm_client
from app.analyzers.prompts import get_narrative_synthesis_prompt
from app.models.signal import Signal
from app.models.narrative import Narrative, NarrativeSource
from app.models.narrative_signal_link import NarrativeSignalLink
from app.models.idea import Idea
from app.models.scraped_content import ScrapedContent
from app.models.data_source import DataSource
from app.config import get_settings
from app.utils.helpers import utcnow
from app.utils.logger import logger

settings = get_settings()


_STAGE2_SYSTEM_PROMPT = (
    "You are a strict JSON generator. "
    "Return ONLY valid JSON with no markdown/code fences and no extra text. "
    "Do not invent sources, quotes, or evidence; only use the provided signal reports."
)


async def run_narrative_synthesis(db: AsyncSession) -> dict:
    """
    Run Stage 2 narrative synthesis.

    1. Gather all signals from the past N days (NARRATIVE_SIGNAL_LOOKBACK_DAYS)
    2. Group signals by source
    3. Send to LLM for narrative detection and idea generation
    4. Store narratives and ideas in database
    """
    now = utcnow()
    start_date = now - timedelta(days=settings.NARRATIVE_SIGNAL_LOOKBACK_DAYS)

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
        logger.info(f"[STAGE 2] No signals found in past {settings.NARRATIVE_SIGNAL_LOOKBACK_DAYS} days — skipping synthesis")
        return {"narratives_created": 0, "ideas_created": 0}

    # Build signal reports grouped by source
    source_signals: dict[str, list[dict]] = {}
    source_id_map: dict[str, int] = {}  # source_name -> data_source_id
    signal_to_source_name: dict[int, str] = {}
    signal_to_source_id: dict[int, int] = {}
    signal_to_content_url: dict[int, str] = {}
    signal_to_title: dict[int, str] = {}

    for signal, content, ds in rows:
        if ds.name not in source_signals:
            source_signals[ds.name] = []
            source_id_map[ds.name] = ds.id

        signal_to_source_name[signal.id] = ds.name
        signal_to_source_id[signal.id] = ds.id
        signal_to_content_url[signal.id] = content.source_url
        signal_to_title[signal.id] = signal.signal_title

        source_signals[ds.name].append({
            "signal_id": signal.id,
            "signal_title": signal.signal_title,
            "description": signal.description,
            "signal_type": signal.signal_type,
            "novelty": signal.novelty,
            "evidence": signal.evidence,
            "related_projects": signal.related_projects,
            "tags": signal.tags,
            "content_url": content.source_url,
            "source_profile_url": ds.url,
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
    prompt = get_narrative_synthesis_prompt().format(
        total_sources=total_sources,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=now.strftime("%Y-%m-%d"),
        all_signal_reports=json.dumps(all_reports, indent=2, default=str),
    )

    logger.info("[STAGE 2] Sending signals to LLM for narrative synthesis...")
    llm_result = await llm_client.generate_json(prompt, system_prompt=_STAGE2_SYSTEM_PROMPT)
    if llm_result is None:
        logger.error("[STAGE 2] LLM returned no result for narrative synthesis")
        return {"narratives_created": 0, "ideas_created": 0}

    narratives_data = llm_result.get("narratives", [])

    # If we have signals but got no narratives, re-ask with a stronger constraint
    if not narratives_data and total_signal_count > 0:
        logger.warning("[STAGE 2] LLM returned 0 narratives; retrying with minimum narrative constraint")
        retry_prompt = (
            prompt
            + "\n\nIMPORTANT:\n"
            + "- If there are any meaningful signals at all, you MUST output at least 1 narrative.\n"
            + "- Each narrative MUST have between 3 and 5 product ideas.\n"
            + "- It is acceptable to mark confidence as 'low' and explain uncertainty.\n"
            + "- Do NOT fabricate evidence; only cite from the provided signal reports.\n"
        )
        llm_result_retry = await llm_client.generate_json(
            retry_prompt, system_prompt=_STAGE2_SYSTEM_PROMPT
        )
        if llm_result_retry is not None:
            llm_result = llm_result_retry
            narratives_data = llm_result.get("narratives", [])

    # Enforce minimum 3 ideas per narrative — drop any that don't meet the bar
    MIN_IDEAS = 3
    MAX_IDEAS = 5
    valid_narratives = []
    for n in narratives_data:
        ideas = n.get("product_ideas", [])
        if len(ideas) < MIN_IDEAS:
            logger.warning(
                f"[STAGE 2] Dropping narrative \"{n.get('title', 'Untitled')}\" — "
                f"only {len(ideas)} idea(s), minimum is {MIN_IDEAS}"
            )
            continue
        if len(ideas) > MAX_IDEAS:
            n["product_ideas"] = ideas[:MAX_IDEAS]
        valid_narratives.append(n)
    narratives_data = valid_narratives

    # Deactivate old narratives that no longer have fresh signals
    await _deactivate_stale_narratives(db)

    # Store new narratives and ideas
    logger.info(f"[STAGE 2] LLM detected {len(narratives_data)} narratives")
    narratives_created = 0
    ideas_created = 0

    for n_data in narratives_data:
        try:
            title = (n_data.get("title") or "Untitled Narrative").strip()
            # Upsert-ish behavior: if a narrative with same title already exists,
            # update it and replace its child rows (ideas, narrative_sources).
            existing_result = await db.execute(
                select(Narrative)
                .where(Narrative.title.ilike(title))
                .order_by(Narrative.last_detected_at.desc())
                .limit(1)
            )
            narrative = existing_result.scalar_one_or_none()
            if narrative:
                narrative.title = title
                narrative.summary = n_data.get("summary", "") or ""
                narrative.confidence = n_data.get("confidence", "low") or "low"
                narrative.confidence_reasoning = n_data.get("confidence_reasoning", "") or ""
                narrative.is_active = True
                narrative.rank = n_data.get("rank")
                narrative.tags = n_data.get("tags", []) or []
                narrative.key_evidence = n_data.get("key_evidence", []) or []
                narrative.supporting_source_names = n_data.get("supporting_sources", []) or []
                narrative.last_detected_at = now
                # Replace children
                narrative.ideas.clear()
                narrative.narrative_sources.clear()
                await db.flush()
            else:
                narrative = Narrative(
                    title=title,
                    summary=n_data.get("summary", "") or "",
                    confidence=n_data.get("confidence", "low") or "low",
                    confidence_reasoning=n_data.get("confidence_reasoning", "") or "",
                    is_active=True,
                    rank=n_data.get("rank"),
                    tags=n_data.get("tags", []) or [],
                    key_evidence=n_data.get("key_evidence", []) or [],
                    supporting_source_names=n_data.get("supporting_sources", []) or [],
                    last_detected_at=now,
                )
                db.add(narrative)
                await db.flush()
            narratives_created += 1
            logger.info(
                f"[STAGE 2]   Narrative #{narratives_created}: \"{narrative.title}\" "
                f"(confidence={narrative.confidence}, tags={narrative.tags})"
            )

            # --- Traceability: link narrative -> signals (ids) -> content URLs ---
            # Prefer explicit IDs from the model. Fall back to IDs referenced in key_evidence objects.
            supporting_ids_raw = n_data.get("supporting_signal_ids") or []
            supporting_ids: list[int] = []
            for x in supporting_ids_raw:
                try:
                    supporting_ids.append(int(x))
                except Exception:
                    continue

            if not supporting_ids:
                for ev in n_data.get("key_evidence", []) or []:
                    if isinstance(ev, dict) and "signal_id" in ev:
                        try:
                            supporting_ids.append(int(ev["signal_id"]))
                        except Exception:
                            pass

            # Keep only signals that were part of this synthesis window
            valid_signal_ids = [sid for sid in supporting_ids if sid in signal_to_source_id]
            if valid_signal_ids:
                # Compute narrative_sources from linked signals (not from LLM source strings)
                ds_counts: dict[int, int] = {}
                for sid in valid_signal_ids:
                    ds_id = signal_to_source_id.get(sid)
                    if ds_id:
                        ds_counts[ds_id] = ds_counts.get(ds_id, 0) + 1
                for ds_id, cnt in ds_counts.items():
                    db.add(NarrativeSource(narrative_id=narrative.id, data_source_id=ds_id, signal_count=cnt))

                # Replace existing links for this narrative (if any) and store new links.
                # If migrations haven't been applied yet, don't fail the whole synthesis run.
                try:
                    await db.execute(
                        sa.delete(NarrativeSignalLink).where(
                            NarrativeSignalLink.narrative_id == narrative.id
                        )
                    )
                    for sid in valid_signal_ids:
                        db.add(NarrativeSignalLink(narrative_id=narrative.id, signal_id=sid))
                except Exception as e:
                    logger.warning(
                        f"[STAGE 2] Could not store narrative-signal links (run migrations?): {e}"
                    )

                # Store supporting_source_names deterministically from linked signals
                narrative.supporting_source_names = sorted(
                    {signal_to_source_name[sid] for sid in valid_signal_ids if sid in signal_to_source_name}
                )

                # Store structured key evidence with URLs where possible
                structured_ev: list[dict] = []
                for ev in n_data.get("key_evidence", []) or []:
                    if isinstance(ev, dict):
                        sid = ev.get("signal_id")
                        try:
                            sid_int = int(sid) if sid is not None else None
                        except Exception:
                            sid_int = None
                        structured_ev.append(
                            {
                                "signal_id": sid_int,
                                "signal_title": signal_to_title.get(sid_int, ev.get("signal_title")) if sid_int else ev.get("signal_title"),
                                "source_name": ev.get("source_name") or (signal_to_source_name.get(sid_int) if sid_int else None),
                                "content_url": ev.get("content_url") or (signal_to_content_url.get(sid_int) if sid_int else None),
                                "evidence": ev.get("evidence") or ev.get("quote") or ev.get("observation"),
                            }
                        )
                    else:
                        structured_ev.append({"evidence": str(ev)})
                if structured_ev:
                    narrative.key_evidence = structured_ev
            else:
                # Fallback behavior: keep whatever the model returned (legacy schema)
                narrative.supporting_source_names = n_data.get("supporting_sources", []) or []
                narrative.key_evidence = n_data.get("key_evidence", []) or []

            # Create ideas (already validated: 3 <= len <= 5)
            idea_list = n_data.get("product_ideas", [])
            logger.info(f"[STAGE 2]     Storing {len(idea_list)} ideas for this narrative")
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
                    # Keep legacy titles for API compatibility; IDs are stored at narrative level.
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
