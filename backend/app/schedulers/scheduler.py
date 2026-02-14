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

    # Twitter scraper — every N hours
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

    # Narrative synthesis — every 14 days at 3 AM UTC
    scheduler.add_job(
        _narrative_synthesis_job,
        trigger=CronTrigger(
            day=f"*/{settings.NARRATIVE_SYNTHESIS_INTERVAL_DAYS}",
            hour=3,
            minute=0,
        ),
        id="narrative_synthesis_periodic",
        name="Fortnightly Narrative Synthesis",
        replace_existing=True,
        misfire_grace_time=7200,  # 2 hours grace
    )
    logger.info(
        f"Scheduled narrative synthesis: every {settings.NARRATIVE_SYNTHESIS_INTERVAL_DAYS} days at 3:00 UTC"
    )

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
