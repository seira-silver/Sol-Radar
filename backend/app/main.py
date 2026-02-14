"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import get_settings
from app.schedulers.scheduler import init_scheduler, start_scheduler, shutdown_scheduler
from app.utils.logger import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: start scheduler on startup, shut down on exit."""
    logger.info("Starting Solana Narrative Detection Backend")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize and start scheduler
    init_scheduler()
    start_scheduler()
    logger.info("Scheduler initialized and started")

    yield

    # Shutdown
    shutdown_scheduler()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Solana Narrative Detection API",
    description=(
        "Detects emerging narratives and early signals within the Solana ecosystem. "
        "Generates actionable product ideas for founders, investors, and ecosystem teams."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.post("/api/v1/trigger/web-scrape", tags=["trigger"])
async def trigger_web_scrape():
    """Manually trigger a web scrape cycle (for development/testing)."""
    from app.schedulers.web_job import web_scrape_job

    logger.info("Manual web scrape triggered via API")
    await web_scrape_job()
    return {"status": "completed", "message": "Web scrape cycle finished"}


@app.post("/api/v1/trigger/twitter-scrape", tags=["trigger"])
async def trigger_twitter_scrape():
    """Manually trigger a Twitter scrape cycle (for development/testing)."""
    from app.schedulers.twitter_job import twitter_scrape_job

    logger.info("Manual Twitter scrape triggered via API")
    await twitter_scrape_job()
    return {"status": "completed", "message": "Twitter scrape cycle finished"}


@app.post("/api/v1/trigger/synthesis", tags=["trigger"])
async def trigger_synthesis():
    """Manually trigger narrative synthesis (for development/testing)."""
    from app.database import async_session_factory
    from app.analyzers.narrative_synthesizer import run_narrative_synthesis

    logger.info("Manual narrative synthesis triggered via API")
    async with async_session_factory() as db:
        result = await run_narrative_synthesis(db)
    return {"status": "completed", "result": result}
