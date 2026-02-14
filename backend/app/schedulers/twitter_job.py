"""Twitter scrape cron job — fetches KOL tweets then runs signal extraction."""

import time

from app.database import async_session_factory
from app.scrapers.twitter_scraper import run_twitter_scrape_cycle, load_kols
from app.analyzers.signal_extractor import run_signal_extraction
from app.utils.logger import logger


async def twitter_scrape_job():
    """
    Full Twitter scraping pipeline:
    1. Fetch latest tweets from all Solana KOLs
    2. Run Stage 1 signal extraction on new tweets
    """
    start_time = time.time()
    kols = load_kols()
    logger.info("=" * 60)
    logger.info("[JOB] STARTING TWITTER SCRAPE JOB")
    logger.info(f"[JOB] KOLs to fetch: {len(kols)}")
    for handle in kols[:10]:
        logger.info(f"[JOB]   - @{handle}")
    if len(kols) > 10:
        logger.info(f"[JOB]   ... and {len(kols) - 10} more")
    logger.info("=" * 60)

    async with async_session_factory() as db:
        try:
            # Step 1: Scrape Twitter KOLs
            scrape_result = await run_twitter_scrape_cycle(db)
            logger.info(
                f"[JOB] Twitter scrape done: {scrape_result.tweets_fetched} fetched, "
                f"{scrape_result.new_content_stored} new, "
                f"{scrape_result.duplicates_skipped} duplicates"
            )
            if scrape_result.errors:
                for err in scrape_result.errors:
                    logger.warning(f"[JOB]   Error: {err}")

            # Step 2: Extract signals from new tweets
            if scrape_result.new_content_stored > 0:
                logger.info(f"[JOB] Running Stage 1 signal extraction on {scrape_result.new_content_stored} new tweets...")
                signal_result = await run_signal_extraction(db)
                logger.info(
                    f"[JOB] Signal extraction done: {signal_result['signals_extracted']} signals "
                    f"from {signal_result['content_processed']} items"
                )
            else:
                logger.info("[JOB] No new tweets — skipping signal extraction")

        except Exception as e:
            logger.error(f"[JOB] Twitter scrape job FAILED: {e}", exc_info=True)

    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"[JOB] TWITTER SCRAPE JOB COMPLETE — took {elapsed:.1f}s")
    logger.info("=" * 60)
