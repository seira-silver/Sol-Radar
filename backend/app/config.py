"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:admin@localhost:5432/solana_narrative"

    # API Keys
    SCRAPEBADGER_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Rate limits
    RATE_LIMIT_SCRAPEBATCHER: int = 5  # requests per second
    RATE_LIMIT_GEMINI_RPM: int = 15  # requests per minute
    RATE_LIMIT_GEMINI_RPD: int = 1500  # requests per day

    # LLM
    LLM_MODEL: str = "gemini/gemini-2.0-flash"

    # Scheduler
    WEB_SCRAPE_HOUR_UTC: int = 2  # 2 AM UTC
    TWITTER_SCRAPE_INTERVAL_HOURS: int = 4
    NARRATIVE_SYNTHESIS_INTERVAL_DAYS: int = 14

    # Scraping
    SCRAPE_DELAY_SECONDS: float = 2.0  # delay between requests to same domain
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30

    # Narrative lifecycle
    NARRATIVE_INACTIVE_AFTER_DAYS: int = 7
    VELOCITY_DECAY_RATE: float = 0.10  # 10% per day

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
