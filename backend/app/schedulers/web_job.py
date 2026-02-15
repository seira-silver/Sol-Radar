"""Web scrape cron job — full pipeline: scrape → Stage 1 → Stage 2.

Pipeline:
  1. Scrape all configured web sources
  2. Stage 1: Signal extraction on new content
  3. Stage 2: Narrative synthesis (aggregates all signals → narratives + ideas)
"""

import time

from app.database import async_session_factory
from app.scrapers.web_scraper import run_web_scrape_cycle, WEB_SOURCES
from app.analyzers.signal_extractor import run_signal_extraction
from app.analyzers.narrative_synthesizer import run_narrative_synthesis
from app.utils.logger import logger


async def web_scrape_job():
    """
    Full web scraping pipeline:
    1. Scrape all configured web sources
    2. Run Stage 1 signal extraction on new content
    3. Run Stage 2 narrative synthesis + idea generation
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("[JOB] STARTING DAILY WEB SCRAPE JOB")
    logger.info("[JOB] Pipeline: Scrape → Stage 1 (signals) → Stage 2 (narratives + ideas)")
    logger.info(f"[JOB] Sources to scrape: {len(WEB_SOURCES)}")
    for src in WEB_SOURCES:
        logger.info(f"[JOB]   - {src['name']} ({src['url'][:60]})")
    logger.info("=" * 60)

    async with async_session_factory() as db:
        try:
            # Step 1: Scrape web sources
            scrape_result = await run_web_scrape_cycle(db)
            logger.info(
                f"[JOB] Web scrape done: {scrape_result.new_content_stored} new items, "
                f"{scrape_result.duplicates_skipped} duplicates, "
                f"{len(scrape_result.errors)} errors"
            )
            if scrape_result.errors:
                for err in scrape_result.errors:
                    logger.warning(f"[JOB]   Error: {err}")

            # Step 2: Stage 1 MUST run before Stage 2 (will no-op if nothing pending)
            logger.info("[JOB] Running Stage 1: Signal extraction on pending content...")
            signal_result = await run_signal_extraction(db)
            logger.info(
                f"[JOB] Signal extraction done: {signal_result['signals_extracted']} signals "
                f"from {signal_result['content_processed']} items"
            )

            # Stage 2: always attempt synthesis (there may be signals from previous runs)
            logger.info("[JOB] Running Stage 2: Narrative synthesis + idea generation...")
            synthesis_result = await run_narrative_synthesis(db)
            logger.info(
                f"[JOB] Stage 2 done: {synthesis_result['narratives_created']} narratives, "
                f"{synthesis_result['ideas_created']} ideas generated"
            )

        except Exception as e:
            logger.error(f"[JOB] Web scrape job FAILED: {e}", exc_info=True)

    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"[JOB] DAILY WEB SCRAPE JOB COMPLETE — took {elapsed:.1f}s")
    logger.info("=" * 60)
