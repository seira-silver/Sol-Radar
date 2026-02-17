"""GitHub Solana repos cron job — search → Stage 1 → Stage 2 → backfill."""

import time

from app.database import async_session_factory
from app.scrapers.github_scraper import run_github_scrape_cycle
from app.analyzers.signal_extractor import run_signal_extraction_for_source_type
from app.analyzers.narrative_synthesizer import run_narrative_synthesis
from app.analyzers.idea_backfiller import run_idea_backfill
from app.utils.logger import logger


async def github_scrape_job():
    """
    Full GitHub pipeline:
      1. Search for Solana-related repos and store summaries
      2. Run Stage 1 signal extraction for source_type="github"
      3. Run Stage 2 narrative synthesis + idea generation
      4. Backfill ideas for under-populated narratives
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("[JOB] STARTING GITHUB SOLANA REPOS JOB")
    logger.info("[JOB] Pipeline: Scrape → Stage 1 (signals) → Stage 2 (narratives + ideas)")
    logger.info("=" * 60)

    async with async_session_factory() as db:
        try:
            scrape_result = await run_github_scrape_cycle(db)
            logger.info(
                "[JOB] GitHub scrape done: "
                f"{scrape_result.repos_fetched} repos, "
                f"{scrape_result.new_content_stored} new, "
                f"{scrape_result.duplicates_skipped} duplicates, "
                f"{len(scrape_result.errors)} errors"
            )
            for err in scrape_result.errors:
                logger.warning(f"[JOB]   Error: {err}")

            logger.info("[JOB] Running Stage 1: Signal extraction for GitHub (source_type='github')...")
            stage1 = await run_signal_extraction_for_source_type(db, source_type="github")
            logger.info(
                "[JOB] Stage 1 done: "
                f"{stage1['content_processed']} items, "
                f"{stage1['signals_extracted']} signals extracted"
            )

            logger.info("[JOB] Running Stage 2: Narrative synthesis + idea generation...")
            synthesis_result = await run_narrative_synthesis(db)
            logger.info(
                "[JOB] Stage 2 done: "
                f"{synthesis_result['narratives_created']} narratives, "
                f"{synthesis_result['ideas_created']} ideas generated"
            )

            logger.info("[JOB] Running Step 4: Idea backfill for under-populated narratives...")
            backfill_result = await run_idea_backfill(db)
            await db.commit()
            logger.info(
                "[JOB] Idea backfill done: "
                f"{backfill_result['ideas_created']} new ideas "
                f"across {backfill_result['narratives_processed']} narrative(s)"
            )

        except Exception as e:
            logger.error(f"[JOB] GitHub job FAILED: {e}", exc_info=True)

    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"[JOB] GITHUB SOLANA REPOS JOB COMPLETE — took {elapsed:.1f}s")
    logger.info("=" * 60)

