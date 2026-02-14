"""Token bucket rate limiter for ScrapeBatcher and Gemini API calls."""

import asyncio
import time
from app.utils.logger import logger


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
            max_tokens: Maximum burst capacity. Defaults to rate (no burst).
            name: Label for logging.
        """
        self.rate = rate
        self.max_tokens = max_tokens or int(rate)
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
                logger.debug(f"[{self.name}] Rate limited — waiting {wait:.2f}s")
                # Release lock while sleeping so other tasks aren't blocked from checking
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

    Free tier: 15 requests/minute, 1500 requests/day.
    """

    def __init__(self, rpm: int = 15, rpd: int = 1500):
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


# Pre-configured instances
scrapebatcher_limiter = TokenBucketRateLimiter(rate=5.0, max_tokens=5, name="scrapebatcher")
gemini_limiter = GeminiRateLimiter(rpm=15, rpd=1500)
