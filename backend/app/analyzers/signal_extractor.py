"""Stage 1: Per-source signal extraction using LLM.

Processes each piece of scraped content individually and extracts
structured signals that indicate emerging Solana ecosystem trends.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzers.llm_client import llm_client
from app.models.scraped_content import ScrapedContent
from app.models.signal import Signal
from app.models.data_source import DataSource
from app.utils.helpers import utcnow
from app.utils.logger import logger


SOURCE_ANALYSIS_PROMPT = """
You are a specialized signal extraction agent for a Solana ecosystem narrative
detection tool. Your job is to read raw content from a single data source and
extract structured signals that may indicate emerging trends, shifts, or
opportunities in the Solana ecosystem.

This tool is built for founders, investors, and ecosystem teams who need to
understand what is starting to matter on Solana BEFORE it becomes obvious.

## Your Source

Source name: {source_name}
Source type: {source_type}
URL: {source_url}
Scraped on: {scrape_date}

## Source Types and What to Look For

- onchain: new program deployments, unusual transaction spikes, new wallet
  behaviors, protocol usage shifts, TVL changes
- developer_blog: new primitives being built, tooling announcements,
  infrastructure shifts, pain points developers are solving
- research_report: quantitative trends, ecosystem comparisons, funding flows,
  developer growth metrics
- social_kol: what influential builders/investors are focused on, frustrations
  they are voicing, projects they are amplifying
- community_forum: grassroots sentiment, repeated questions or complaints,
  projects gaining organic traction, narratives forming bottom-up
- mobile: new dApp Store listings, mobile-native behaviors, consumer adoption
  signals from Solana Mobile ecosystem

## Instructions

1. Read the content carefully
2. Extract only signals that are NOVEL, SPECIFIC, and SOLANA-RELEVANT
3. Ignore generic crypto market commentary, price talk, or anything not
   specific to Solana ecosystem activity
4. A signal must point to something CHANGING or EMERGING — not stable
   background facts
5. Rate each signal's strength honestly — most content will yield low signals

Return ONLY valid JSON. No markdown, no explanation outside the JSON.

## Output Schema

{{
  "source_name": "{source_name}",
  "source_url": "{source_url}",
  "source_type": "{source_type}",
  "scrape_date": "{scrape_date}",
  "signals": [
    {{
      "signal_title": "Brief label for the signal",
      "description": "What specifically is happening or changing",
      "signal_type": "onchain | developer | social | research | mobile | other",
      "novelty": "high | medium | low",
      "evidence": "Direct quote, metric, or specific observation from the content",
      "related_projects_or_protocols": ["project1", "protocol2"],
      "tags": ["defi", "infrastructure", "consumer", "gaming", "mobile", "hackathon"]
    }}
  ],
  "total_signals_found": 0,
  "source_quality": "high | medium | low",
  "notes": "Optional: anything unusual about this source or its content"
}}

If no meaningful signals are found, return an empty signals array.

## Raw Content Below

--- START ---
{raw_content}
--- END ---
"""


async def extract_signals_for_content(
    db: AsyncSession, content: ScrapedContent
) -> int:
    """
    Run Stage 1 signal extraction on a single piece of scraped content.

    Returns the number of signals extracted.
    """
    # Load associated data source
    ds_result = await db.execute(
        select(DataSource).where(DataSource.id == content.data_source_id)
    )
    ds = ds_result.scalar_one_or_none()
    if not ds:
        logger.error(f"DataSource not found for content {content.id}")
        return 0

    # Build prompt
    prompt = SOURCE_ANALYSIS_PROMPT.format(
        source_name=ds.name,
        source_type=ds.source_category,
        source_url=content.source_url,
        scrape_date=content.scraped_at.isoformat() if content.scraped_at else utcnow().isoformat(),
        raw_content=content.raw_content,
    )

    # Call LLM
    result = await llm_client.generate_json(prompt)
    if result is None:
        logger.warning(f"LLM returned no result for content {content.id}")
        content.is_analyzed = True
        await db.flush()
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

    content.is_analyzed = True
    await db.flush()

    logger.info(
        f"Extracted {signals_stored} signals from content {content.id} "
        f"({ds.name}: {content.source_url[:60]})"
    )
    return signals_stored


async def run_signal_extraction(db: AsyncSession) -> dict:
    """
    Run Stage 1 signal extraction on all unanalyzed content.

    Returns summary stats.
    """
    # Find all unanalyzed content
    result = await db.execute(
        select(ScrapedContent).where(ScrapedContent.is_analyzed == False).order_by(  # noqa: E712
            ScrapedContent.scraped_at.desc()
        )
    )
    unanalyzed = result.scalars().all()

    if not unanalyzed:
        logger.info("No unanalyzed content found — skipping signal extraction")
        return {"content_processed": 0, "signals_extracted": 0}

    logger.info(f"[STAGE 1] Running signal extraction on {len(unanalyzed)} unanalyzed items")

    total_signals = 0
    processed = 0

    for idx, content in enumerate(unanalyzed):
        try:
            logger.info(f"[STAGE 1] [{idx + 1}/{len(unanalyzed)}] Analyzing: {content.title or content.source_url[:60]}")
            count = await extract_signals_for_content(db, content)
            total_signals += count
            processed += 1
            if count > 0:
                logger.info(f"[STAGE 1]   Found {count} signals")
            else:
                logger.info(f"[STAGE 1]   No signals found")
        except Exception as e:
            logger.error(f"[STAGE 1]   FAILED content {content.id}: {e}")
            content.is_analyzed = True  # Mark to avoid re-processing bad content
            await db.flush()

    await db.commit()

    summary = {
        "content_processed": processed,
        "signals_extracted": total_signals,
    }
    logger.info(f"Stage 1 complete: {summary}")
    return summary
