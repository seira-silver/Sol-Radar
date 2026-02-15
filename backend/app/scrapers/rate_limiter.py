"""Token bucket rate limiter for ScrapeBadger and LLM API calls."""

import asyncio
import time
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()


class TokenBucketRateLimiter:
    """
    Async token bucket rate limiter.

    Tokens are replenished at a fixed rate. Each request consumes one token.
    If no tokens are available, the caller awaits until one is replenished.
    """

    def __init__(self, rate: float, max_tokens: int | None = None, name: str = "default"):
        """
        Args:
            rate: Tokens per second to replenish.
            max_tokens: Maximum burst capacity. Defaults to ceil(rate) (no burst).
            name: Label for logging.
        """
        self.rate = rate
        self.max_tokens = max_tokens or max(1, int(rate))
        self.name = name
        self._tokens = float(self.max_tokens)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a token is available, then consume it."""
        async with self._lock:
            while True:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                # Calculate wait time for next token
                wait = (1.0 - self._tokens) / self.rate
                logger.info(f"[{self.name}] Rate limited — waiting {wait:.1f}s")
                # Release lock while sleeping so other tasks aren't blocked
                self._lock.release()
                await asyncio.sleep(wait)
                await self._lock.acquire()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.max_tokens, self._tokens + elapsed * self.rate)
        self._last_refill = now


class GeminiRateLimiter:
    """
    Dual rate limiter for Gemini free tier: RPM + RPD limits.
    """

    def __init__(self, rpm: int, rpd: int):
        self._minute_limiter = TokenBucketRateLimiter(
            rate=rpm / 60.0, max_tokens=rpm, name="gemini-rpm"
        )
        self._day_limiter = TokenBucketRateLimiter(
            rate=rpd / 86400.0, max_tokens=rpd, name="gemini-rpd"
        )
        self._request_count = 0

    async def acquire(self) -> None:
        """Wait for both RPM and RPD limits to allow a request."""
        await self._minute_limiter.acquire()
        await self._day_limiter.acquire()
        self._request_count += 1

    @property
    def total_requests(self) -> int:
        return self._request_count


# ── Pre-configured instances (read from config) ──────────────────────────

# ScrapeBadger: free tier = 5 RPM → rate = 5/60 tokens per second
scrapebadger_limiter = TokenBucketRateLimiter(
    rate=settings.SCRAPEBADGER_RPM / 60.0,
    max_tokens=settings.SCRAPEBADGER_RPM,
    name="scrapebadger",
)
logger.info(
    f"ScrapeBadger rate limiter: {settings.SCRAPEBADGER_RPM} RPM "
    f"({settings.SCRAPEBADGER_RPM / 60.0:.3f} req/sec)"
)

# Gemini: free tier = 15 RPM, 1500 RPD
gemini_limiter = GeminiRateLimiter(
    rpm=settings.GEMINI_RPM,
    rpd=settings.GEMINI_RPD,
)
logger.info(
    f"Gemini rate limiter: {settings.GEMINI_RPM} RPM, {settings.GEMINI_RPD} RPD"
)

# xAI: defaults are conservative; tune via XAI_RPM / XAI_RPD in .env
xai_limiter = GeminiRateLimiter(
    rpm=settings.XAI_RPM,
    rpd=settings.XAI_RPD,
)
logger.info(
    f"xAI rate limiter: {settings.XAI_RPM} RPM, {settings.XAI_RPD} RPD"
)
