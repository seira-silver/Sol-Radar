"""Stage 1: Per-source signal extraction using LLM.

Processes each piece of scraped content individually and extracts
structured signals that indicate emerging Solana ecosystem trends.

Uses a status state machine on ScrapedContent to prevent double-analysis:
  pending → processing → completed / failed / skipped

Only content with status='pending' (or 'failed' below MAX_ANALYSIS_ATTEMPTS)
is picked up for analysis.
"""

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzers.llm_client import llm_client
from app.analyzers.prompts import get_source_analysis_prompt
from app.models.scraped_content import ScrapedContent, MAX_ANALYSIS_ATTEMPTS
from app.models.signal import Signal
from app.models.data_source import DataSource
from app.utils.helpers import utcnow
from app.utils.logger import logger


_STAGE1_SYSTEM_PROMPT = (
    "You are a strict JSON generator. "
    "Return ONLY valid JSON with no markdown/code fences and no extra text. "
    "Do not invent facts; only use the provided raw content."
)


def _mark_processing(content: ScrapedContent) -> None:
    """Transition: pending/failed → processing."""
    content.analysis_status = "processing"
    content.analysis_attempts += 1


def _mark_completed(content: ScrapedContent) -> None:
    """Transition: processing → completed."""
    content.analysis_status = "completed"
    content.analyzed_at = utcnow()
    content.analysis_error = None


def _mark_failed(content: ScrapedContent, error: str) -> None:
    """Transition: processing → failed (retryable if under MAX_ANALYSIS_ATTEMPTS)."""
    if content.analysis_attempts >= MAX_ANALYSIS_ATTEMPTS:
        content.analysis_status = "skipped"  # give up after max attempts
        logger.warning(
            f"Content {content.id} exceeded {MAX_ANALYSIS_ATTEMPTS} attempts — marking as skipped"
        )
    else:
        content.analysis_status = "failed"
    content.analysis_error = error[:500]  # truncate long errors
    content.analyzed_at = utcnow()


def _mark_skipped(content: ScrapedContent, reason: str) -> None:
    """Transition: pending → skipped (content not worth analyzing)."""
    content.analysis_status = "skipped"
    content.analysis_error = reason
    content.analyzed_at = utcnow()


async def extract_signals_for_content(
    db: AsyncSession, content: ScrapedContent
) -> int:
    """
    Run Stage 1 signal extraction on a single piece of scraped content.

    State machine: pending → processing → completed/failed
    Returns the number of signals extracted.
    """
    # Guard: only analyze if pending or retryable failed
    if content.analysis_status == "completed":
        logger.info(f"Content {content.id} already analyzed — skipping")
        return 0
    if content.analysis_status == "skipped":
        logger.info(f"Content {content.id} marked as skipped — skipping")
        return 0
    if content.analysis_status == "failed" and content.analysis_attempts >= MAX_ANALYSIS_ATTEMPTS:
        logger.info(f"Content {content.id} exceeded max attempts — skipping")
        return 0

    # Skip very short content (not worth an LLM call)
    if len(content.raw_content.strip()) < 50:
        _mark_skipped(content, "Content too short (<50 chars)")
        await db.flush()
        return 0

    # Load associated data source
    ds_result = await db.execute(
        select(DataSource).where(DataSource.id == content.data_source_id)
    )
    ds = ds_result.scalar_one_or_none()
    if not ds:
        logger.error(f"DataSource not found for content {content.id}")
        _mark_skipped(content, "DataSource not found")
        await db.flush()
        return 0

    # ── Mark as processing ──
    _mark_processing(content)
    await db.flush()

    # Build prompt
    prompt = get_source_analysis_prompt().format(
        source_name=ds.name,
        source_type=ds.source_category,
        source_url=content.source_url,
        scrape_date=content.scraped_at.isoformat() if content.scraped_at else utcnow().isoformat(),
        raw_content=content.raw_content,
    )

    # Call LLM
    try:
        result = await llm_client.generate_json(prompt, system_prompt=_STAGE1_SYSTEM_PROMPT)
    except Exception as e:
        _mark_failed(content, str(e))
        await db.flush()
        logger.error(f"LLM call failed for content {content.id}: {e}")
        return 0

    if result is None:
        _mark_failed(content, "LLM returned None")
        await db.flush()
        logger.warning(f"LLM returned no result for content {content.id}")
        return 0

    # Parse and store signals
    signals_data = result.get("signals", [])
    signals_stored = 0

    for sig in signals_data:
        try:
            signal = Signal(
                scraped_content_id=content.id,
                signal_title=sig.get("signal_title", "Unknown signal"),
                description=sig.get("description", ""),
                signal_type=sig.get("signal_type", "other"),
                novelty=sig.get("novelty", "low"),
                evidence=sig.get("evidence", ""),
                related_projects=sig.get("related_projects_or_protocols", []),
                tags=sig.get("tags", []),
            )
            db.add(signal)
            signals_stored += 1
        except Exception as e:
            logger.error(f"Error storing signal: {e}")

    # ── Mark as completed ──
    _mark_completed(content)
    await db.flush()

    logger.info(
        f"[STAGE 1] Extracted {signals_stored} signals from content {content.id} "
        f"({ds.name}: {content.source_url[:60]})"
    )
    return signals_stored


async def run_signal_extraction(db: AsyncSession) -> dict:
    """
    Run Stage 1 signal extraction on all pending/retryable content.

    Only picks up:
    - analysis_status = 'pending'
    - analysis_status = 'failed' with analysis_attempts < MAX_ANALYSIS_ATTEMPTS

    Returns summary stats.
    """
    result = await db.execute(
        select(ScrapedContent).where(
            or_(
                ScrapedContent.analysis_status == "pending",
                (
                    (ScrapedContent.analysis_status == "failed")
                    & (ScrapedContent.analysis_attempts < MAX_ANALYSIS_ATTEMPTS)
                ),
            )
        ).order_by(ScrapedContent.scraped_at.desc())
    )
    to_analyze = result.scalars().all()

    if not to_analyze:
        logger.info("[STAGE 1] No pending content — skipping signal extraction")
        return {"content_processed": 0, "signals_extracted": 0}

    logger.info(f"[STAGE 1] Running signal extraction on {len(to_analyze)} items")

    total_signals = 0
    processed = 0

    for idx, content in enumerate(to_analyze):
        try:
            logger.info(
                f"[STAGE 1] [{idx + 1}/{len(to_analyze)}] Analyzing: "
                f"{content.title or content.source_url[:60]} "
                f"(attempt {content.analysis_attempts + 1})"
            )
            count = await extract_signals_for_content(db, content)
            total_signals += count
            processed += 1
            if count > 0:
                logger.info(f"[STAGE 1]   Found {count} signals")
            else:
                logger.info(f"[STAGE 1]   No signals found")
        except Exception as e:
            logger.error(f"[STAGE 1]   FAILED content {content.id}: {e}")
            _mark_failed(content, str(e))
            await db.flush()

    await db.commit()

    summary = {
        "content_processed": processed,
        "signals_extracted": total_signals,
    }
    logger.info(f"[STAGE 1] Complete: {summary}")
    return summary


async def run_signal_extraction_for_source_type(
    db: AsyncSession, source_type: str, max_items: int | None = None
) -> dict:
    """
    Run Stage 1 on pending/retryable content limited to a DataSource source_type
    (e.g. "twitter") so we don't burn LLM credits analyzing unrelated backlog.
    """
    q = (
        select(ScrapedContent)
        .join(DataSource, ScrapedContent.data_source_id == DataSource.id)
        .where(
            DataSource.source_type == source_type,
            or_(
                ScrapedContent.analysis_status == "pending",
                (
                    (ScrapedContent.analysis_status == "failed")
                    & (ScrapedContent.analysis_attempts < MAX_ANALYSIS_ATTEMPTS)
                ),
            ),
        )
        .order_by(ScrapedContent.scraped_at.desc())
    )
    if max_items is not None and max_items > 0:
        q = q.limit(max_items)

    result = await db.execute(q)
    to_analyze = result.scalars().all()

    if not to_analyze:
        logger.info(f"[STAGE 1] No pending content for source_type='{source_type}' — skipping")
        return {"content_processed": 0, "signals_extracted": 0, "source_type": source_type}

    logger.info(
        f"[STAGE 1] Running signal extraction on {len(to_analyze)} items (source_type='{source_type}')"
    )

    total_signals = 0
    processed = 0

    for idx, content in enumerate(to_analyze):
        try:
            logger.info(
                f"[STAGE 1] [{idx + 1}/{len(to_analyze)}] Analyzing: "
                f"{content.title or content.source_url[:60]} "
                f"(attempt {content.analysis_attempts + 1})"
            )
            count = await extract_signals_for_content(db, content)
            total_signals += count
            processed += 1
        except Exception as e:
            logger.error(f"[STAGE 1]   FAILED content {content.id}: {e}")
            _mark_failed(content, str(e))
            await db.flush()

    await db.commit()
    summary = {
        "content_processed": processed,
        "signals_extracted": total_signals,
        "source_type": source_type,
    }
    logger.info(f"[STAGE 1] Complete (filtered): {summary}")
    return summary
