"""CoinGecko scrape cron job — trending coins → Stage 1 → Stage 2 → backfill."""

import time

from app.database import async_session_factory
from app.scrapers.coingecko_scraper import run_coingecko_scrape_cycle
from app.analyzers.signal_extractor import run_signal_extraction_for_source_type
from app.analyzers.narrative_synthesizer import run_narrative_synthesis
from app.analyzers.idea_backfiller import run_idea_backfill
from app.utils.logger import logger


async def coingecko_scrape_job():
    """
    Full CoinGecko pipeline:
      1. Fetch trending coins and store as ScrapedContent
      2. Run Stage 1 signal extraction for source_type="api"
      3. Run Stage 2 narrative synthesis + idea generation
      4. Backfill ideas for under-populated narratives
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("[JOB] STARTING COINGECKO TRENDING JOB")
    logger.info("[JOB] Pipeline: Scrape → Stage 1 (signals) → Stage 2 (narratives + ideas)")
    logger.info("=" * 60)

    async with async_session_factory() as db:
        try:
            scrape_result = await run_coingecko_scrape_cycle(db)
            logger.info(
                "[JOB] CoinGecko scrape done: "
                f"{scrape_result.items_fetched} items, "
                f"{scrape_result.new_content_stored} new, "
                f"{scrape_result.duplicates_skipped} duplicates, "
                f"{len(scrape_result.errors)} errors"
            )
            for err in scrape_result.errors:
                logger.warning(f"[JOB]   Error: {err}")

            # Stage 1: restrict to DataSource.source_type="api"
            logger.info("[JOB] Running Stage 1: Signal extraction for CoinGecko (source_type='api')...")
            stage1 = await run_signal_extraction_for_source_type(db, source_type="api")
            logger.info(
                "[JOB] Stage 1 done: "
                f"{stage1['content_processed']} items, "
                f"{stage1['signals_extracted']} signals extracted"
            )

            # Stage 2: narrative synthesis
            logger.info("[JOB] Running Stage 2: Narrative synthesis + idea generation...")
            synthesis_result = await run_narrative_synthesis(db)
            logger.info(
                "[JOB] Stage 2 done: "
                f"{synthesis_result['narratives_created']} narratives, "
                f"{synthesis_result['ideas_created']} ideas generated"
            )

            # Idea backfill
            logger.info("[JOB] Running Step 4: Idea backfill for under-populated narratives...")
            backfill_result = await run_idea_backfill(db)
            await db.commit()
            logger.info(
                "[JOB] Idea backfill done: "
                f"{backfill_result['ideas_created']} new ideas "
                f"across {backfill_result['narratives_processed']} narrative(s)"
            )

        except Exception as e:
            logger.error(f"[JOB] CoinGecko job FAILED: {e}", exc_info=True)

    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"[JOB] COINGECKO TRENDING JOB COMPLETE — took {elapsed:.1f}s")
    logger.info("=" * 60)

