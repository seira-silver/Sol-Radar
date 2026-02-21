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

    # External data providers
    # CoinGecko
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    # Some CoinGecko endpoints may require an API key; keep it optional.
    COINGECKO_API_KEY: str = ""
    # Dune Analytics
    DUNE_API_KEY: str = ""
    DUNE_BASE_URL: str = "https://api.dune.com/api/v1"
    # GitHub
    GITHUB_TOKEN: str = ""
    GITHUB_BASE_URL: str = "https://api.github.com"

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
    WEB_SCRAPE_INTERVAL_HOURS: int = 8  # every 3 hours
    TWITTER_SCRAPE_INTERVAL_HOURS: int = 24  # every 24 hours
    NARRATIVE_SYNTHESIS_INTERVAL_DAYS: int = 1
    # New source-specific schedulers
    COINGECKO_SCRAPE_INTERVAL_HOURS: int = 8  # trending coins can change quickly
    DUNE_SCRAPE_INTERVAL_HOURS: int = 8  # on-chain trend queries are heavier
    GITHUB_SCRAPE_INTERVAL_HOURS: int = 8  # repo activity does not need hourly polling
    NARRATIVE_SIGNAL_LOOKBACK_DAYS: int = 7  # how many days of signals to consider during synthesis

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
