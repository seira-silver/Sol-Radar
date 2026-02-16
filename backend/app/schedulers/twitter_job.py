"""Twitter scrape cron job — full pipeline: scrape → Stage 1 → Stage 2 → backfill.

Pipeline:
  1. Scrape KOL tweets (per-KOL with rate limiting)
  2. Stage 1: Signal extraction (inline per KOL after each fetch)
  3. Stage 2: Narrative synthesis (aggregates all signals → narratives + ideas)
  4. Idea backfill: top up any narratives that still have < 3 ideas
"""

import time

from app.database import async_session_factory
from app.scrapers.twitter_scraper import run_twitter_scrape_cycle, load_kols
from app.analyzers.narrative_synthesizer import run_narrative_synthesis
from app.analyzers.signal_extractor import run_signal_extraction_for_source_type
from app.analyzers.idea_backfiller import run_idea_backfill
from app.utils.logger import logger


async def twitter_scrape_job():
    """
    Full Twitter pipeline: scrape → Stage 1 (per-KOL) → Stage 2 (synthesis).
    """
    start_time = time.time()
    kols = load_kols()
    logger.info("=" * 60)
    logger.info("[JOB] STARTING TWITTER SCRAPE JOB")
    logger.info("[JOB] Pipeline: Scrape → Stage 1 (signals) → Stage 2 (narratives + ideas)")
    logger.info(f"[JOB] KOLs to fetch: {len(kols)}")
    for handle in kols[:10]:
        logger.info(f"[JOB]   - @{handle}")
    if len(kols) > 10:
        logger.info(f"[JOB]   ... and {len(kols) - 10} more")
    logger.info("=" * 60)

    async with async_session_factory() as db:
        try:
            scrape_result = await run_twitter_scrape_cycle(db)
            logger.info(
                f"[JOB] Twitter scrape done: {scrape_result.tweets_fetched} fetched, "
                f"{scrape_result.new_content_stored} new, "
                f"{scrape_result.duplicates_skipped} duplicates, "
                f"{scrape_result.signals_extracted} signals extracted"
            )
            if scrape_result.errors:
                for err in scrape_result.errors:
                    logger.warning(f"[JOB]   Error: {err}")

            # Stage 1 MUST always run before Stage 2.
            logger.info("[JOB] Running Stage 1: Signal extraction (twitter)...")
            stage1 = await run_signal_extraction_for_source_type(db, source_type="twitter")
            logger.info(
                f"[JOB] Stage 1 done: {stage1['content_processed']} items, "
                f"{stage1['signals_extracted']} signals extracted"
            )

            # Stage 2: attempt synthesis (there may be signals from previous runs)
            logger.info("[JOB] Running Stage 2: Narrative synthesis + idea generation...")
            synthesis_result = await run_narrative_synthesis(db)
            logger.info(
                f"[JOB] Stage 2 done: {synthesis_result['narratives_created']} narratives, "
                f"{synthesis_result['ideas_created']} ideas generated"
            )

            # Step 4: Backfill ideas for any narratives that still have < 3
            logger.info("[JOB] Running Step 4: Idea backfill for under-populated narratives...")
            backfill_result = await run_idea_backfill(db)
            await db.commit()
            logger.info(
                f"[JOB] Idea backfill done: {backfill_result['ideas_created']} new ideas "
                f"across {backfill_result['narratives_processed']} narrative(s)"
            )

        except Exception as e:
            logger.error(f"[JOB] Twitter scrape job FAILED: {e}", exc_info=True)

    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"[JOB] TWITTER SCRAPE JOB COMPLETE — took {elapsed:.1f}s")
    logger.info("=" * 60)
