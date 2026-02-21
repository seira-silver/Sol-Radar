"""APScheduler setup — configures and starts all cron jobs."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings
from app.schedulers.web_job import web_scrape_job
from app.schedulers.twitter_job import twitter_scrape_job
from app.schedulers.coingecko_job import coingecko_scrape_job
from app.schedulers.dune_job import dune_scrape_job
from app.schedulers.github_job import github_scrape_job
from app.utils.logger import logger

settings = get_settings()

scheduler = AsyncIOScheduler(timezone="UTC")


def init_scheduler() -> AsyncIOScheduler:
    """Configure and return the scheduler with all jobs."""

    # Web scraper — every N hours (default: 3h)
    scheduler.add_job(
        web_scrape_job,
        trigger=IntervalTrigger(hours=settings.WEB_SCRAPE_INTERVAL_HOURS),
        id="web_scrape_periodic",
        name="Periodic Web Scraper",
        replace_existing=True,
        misfire_grace_time=3600,  # 1 hour grace
    )
    logger.info(f"Scheduled web scrape job: every {settings.WEB_SCRAPE_INTERVAL_HOURS} hours")

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

  # CoinGecko trending — every N hours (default: 1h)
    scheduler.add_job(
        coingecko_scrape_job,
        trigger=IntervalTrigger(hours=settings.COINGECKO_SCRAPE_INTERVAL_HOURS),
        id="coingecko_trending_periodic",
        name="CoinGecko Trending Scraper",
        replace_existing=True,
        misfire_grace_time=3600,  # 1 hour grace
    )
    logger.info(
        f"Scheduled CoinGecko trending job: every {settings.COINGECKO_SCRAPE_INTERVAL_HOURS} hours"
    )

    # Narrative synthesis — daily at 3 AM UTC
    scheduler.add_job(
        _narrative_synthesis_job,
        trigger=CronTrigger(
            hour=8,
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
        trigger=IntervalTrigger(hours=8),
        id="idea_backfill_hourly",
        name="Hourly Idea Backfill",
        replace_existing=True,
        misfire_grace_time=1800,  # 30 min grace
    )
    logger.info("Scheduled idea backfill: every 1 hour")

    # Dune on-chain trending — every N hours (default: 3h)
    scheduler.add_job(
        dune_scrape_job,
        trigger=IntervalTrigger(hours=settings.DUNE_SCRAPE_INTERVAL_HOURS),
        id="dune_trending_periodic",
        name="Dune Trending Scraper",
        replace_existing=True,
        misfire_grace_time=3600,  # 1 hour grace
    )
    logger.info(
        f"Scheduled Dune trending job: every {settings.DUNE_SCRAPE_INTERVAL_HOURS} hours"
    )

    # GitHub Solana repos — every N hours (default: 6h)
    scheduler.add_job(
        github_scrape_job,
        trigger=IntervalTrigger(hours=settings.GITHUB_SCRAPE_INTERVAL_HOURS),
        id="github_solana_periodic",
        name="GitHub Solana Repos Scraper",
        replace_existing=True,
        misfire_grace_time=3600,  # 1 hour grace
    )
    logger.info(
        f"Scheduled GitHub Solana job: every {settings.GITHUB_SCRAPE_INTERVAL_HOURS} hours"
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


async def _idea_backfill_job():
    """Hourly job: find narratives with < 3 ideas and generate more via LLM."""
    from app.database import async_session_factory
    from app.analyzers.idea_backfiller import run_idea_backfill

    logger.info("Starting hourly idea backfill job")
    async with async_session_factory() as db:
        try:
            result = await run_idea_backfill(db)
            await db.commit()
            logger.info(f"Idea backfill complete: {result}")
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
