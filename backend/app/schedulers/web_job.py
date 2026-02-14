"""Web scrape cron job — scrapes all web sources then runs signal extraction."""

import time

from app.database import async_session_factory
from app.scrapers.web_scraper import run_web_scrape_cycle, WEB_SOURCES
from app.analyzers.signal_extractor import run_signal_extraction
from app.utils.logger import logger


async def web_scrape_job():
    """
    Full web scraping pipeline:
    1. Scrape all configured web sources
    2. Run Stage 1 signal extraction on new content
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("[JOB] STARTING DAILY WEB SCRAPE JOB")
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

            # Step 2: Extract signals from new content
            if scrape_result.new_content_stored > 0:
                logger.info(f"[JOB] Running Stage 1 signal extraction on {scrape_result.new_content_stored} new items...")
                signal_result = await run_signal_extraction(db)
                logger.info(
                    f"[JOB] Signal extraction done: {signal_result['signals_extracted']} signals "
                    f"from {signal_result['content_processed']} items"
                )
            else:
                logger.info("[JOB] No new content — skipping signal extraction")

        except Exception as e:
            logger.error(f"[JOB] Web scrape job FAILED: {e}", exc_info=True)

    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"[JOB] DAILY WEB SCRAPE JOB COMPLETE — took {elapsed:.1f}s")
    logger.info("=" * 60)
