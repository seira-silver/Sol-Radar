"""APScheduler setup — configures and starts all cron jobs."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings
from app.schedulers.web_job import web_scrape_job
from app.schedulers.twitter_job import twitter_scrape_job
from app.utils.logger import logger

settings = get_settings()

scheduler = AsyncIOScheduler(timezone="UTC")


def init_scheduler() -> AsyncIOScheduler:
    """Configure and return the scheduler with all jobs."""

    # Web scraper — daily at configured hour UTC
    scheduler.add_job(
        web_scrape_job,
        trigger=CronTrigger(hour=settings.WEB_SCRAPE_HOUR_UTC, minute=0),
        id="web_scrape_daily",
        name="Daily Web Scraper",
        replace_existing=True,
        misfire_grace_time=3600,  # 1 hour grace
    )
    logger.info(f"Scheduled web scrape job: daily at {settings.WEB_SCRAPE_HOUR_UTC}:00 UTC")

    # Twitter scraper — every N hours (default: 72h = 3 days)
    scheduler.add_job(
        twitter_scrape_job,
        trigger=IntervalTrigger(hours=settings.TWITTER_SCRAPE_INTERVAL_HOURS),
        id="twitter_scrape_periodic",
        name="Periodic Twitter Scraper",
        replace_existing=True,
        misfire_grace_time=1800,  # 30 min grace
    )
    logger.info(
        f"Scheduled Twitter scrape job: every {settings.TWITTER_SCRAPE_INTERVAL_HOURS} hours"
    )

    # Narrative synthesis — daily at 3 AM UTC
    scheduler.add_job(
        _narrative_synthesis_job,
        trigger=CronTrigger(
            hour=3,
            minute=0,
        ),
        id="narrative_synthesis_daily",
        name="Daily Narrative Synthesis",
        replace_existing=True,
        misfire_grace_time=3600,  # 1 hour grace
    )
    logger.info("Scheduled narrative synthesis: daily at 3:00 UTC")

    # Idea backfill — hourly, tops up narratives that have < 3 ideas
    scheduler.add_job(
        _idea_backfill_job,
        trigger=IntervalTrigger(hours=1),
        id="idea_backfill_hourly",
        name="Hourly Idea Backfill",
        replace_existing=True,
        misfire_grace_time=1800,  # 30 min grace
    )
    logger.info("Scheduled idea backfill: every 1 hour")

    return scheduler


async def _narrative_synthesis_job():
    """Wrapper for narrative synthesis that creates its own DB session."""
    from app.database import async_session_factory
    from app.analyzers.narrative_synthesizer import run_narrative_synthesis

    logger.info("Starting scheduled narrative synthesis job")
    async with async_session_factory() as db:
        try:
            result = await run_narrative_synthesis(db)
            logger.info(f"Narrative synthesis complete: {result}")
        except Exception as e:
            logger.error(f"Narrative synthesis job failed: {e}")


async def _idea_backfill_job():
    """Hourly job: find narratives with < 3 ideas and generate more via LLM."""
    from app.database import async_session_factory
    from scripts.backfill_ideas import backfill_narrative, MIN_IDEAS

    from sqlalchemy import select, func
    from app.models.narrative import Narrative
    from app.models.idea import Idea

    logger.info("Starting hourly idea backfill job")
    async with async_session_factory() as db:
        try:
            idea_count_sq = (
                select(
                    Idea.narrative_id,
                    func.count(Idea.id).label("idea_count"),
                )
                .group_by(Idea.narrative_id)
                .subquery()
            )
            result = await db.execute(
                select(Narrative)
                .outerjoin(idea_count_sq, Narrative.id == idea_count_sq.c.narrative_id)
                .where(
                    Narrative.is_active == True,  # noqa: E712
                    (idea_count_sq.c.idea_count < MIN_IDEAS) | (idea_count_sq.c.idea_count.is_(None)),
                )
                .order_by(Narrative.id)
            )
            narratives = list(result.scalars().all())

            if not narratives:
                logger.info("Idea backfill: all narratives have >= 3 ideas, nothing to do")
                return

            logger.info(f"Idea backfill: found {len(narratives)} narrative(s) needing ideas")
            total_created = 0
            for narrative in narratives:
                try:
                    created = await backfill_narrative(db, narrative, dry_run=False)
                    total_created += created
                except Exception as e:
                    logger.error(f"Idea backfill error on narrative #{narrative.id}: {e}")

            await db.commit()
            logger.info(f"Idea backfill complete: {total_created} new idea(s) across {len(narratives)} narrative(s)")
        except Exception as e:
            logger.error(f"Idea backfill job failed: {e}")


def start_scheduler():
    """Start the scheduler if not already running."""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started — next job fire times:")
        for job in scheduler.get_jobs():
            logger.info(f"  {job.name}: next run at {job.next_run_time}")


def shutdown_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
