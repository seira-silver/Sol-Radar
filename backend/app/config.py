"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:admin@localhost:5432/solana_narrative"

    # API Keys
    SCRAPEBADGER_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    # xAI (Grok)
    # LiteLLM expects `XAI_API_KEY` env var; we also accept `GROK_API_KEY`.
    XAI_API_KEY: str = ""
    GROK_API_KEY: str = ""

    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Rate limits — adjust these when you upgrade tiers
    SCRAPEBADGER_RPM: int = 5  # requests per minute (free tier = 5)
    GEMINI_RPM: int = 15  # requests per minute (free tier = 15)
    GEMINI_RPD: int = 1500  # requests per day (free tier = 1500)
    # xAI defaults (conservative). Adjust based on your plan.
    XAI_RPM: int = 60
    XAI_RPD: int = 100000

    # LLM
    # Default to Grok to avoid Gemini free-tier throttling.
    LLM_MODEL: str = "xai/grok-4-1-fast-non-reasoning"

    # Scheduler
    WEB_SCRAPE_HOUR_UTC: int = 2  # 2 AM UTC
    # Twitter scrape is expensive (ScrapeBadger credits). Default: every 3 days.
    TWITTER_SCRAPE_INTERVAL_HOURS: int = 72
    NARRATIVE_SYNTHESIS_INTERVAL_DAYS: int = 14

    # Scraping
    SCRAPE_DELAY_SECONDS: float = 2.0  # delay between requests to same domain
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30

    # Twitter scraping behavior
    # How many recent tweets to store per KOL per scrape cycle (prefers originals).
    TWITTER_TWEETS_PER_KOL: int = 3

    # Narrative lifecycle
    NARRATIVE_INACTIVE_AFTER_DAYS: int = 7
    VELOCITY_DECAY_RATE: float = 0.10  # 10% per day

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
