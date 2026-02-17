"""CoinGecko trending coins scraper.

Fetches trending coins from the public CoinGecko API and stores them as
ScrapedContent rows so they can flow through Stage 1 → Stage 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.data_source import DataSource
from app.models.scraped_content import ScrapedContent
from app.utils.helpers import content_hash, truncate_text, clean_text, utcnow
from app.utils.logger import logger

settings = get_settings()


@dataclass
class CoinGeckoScrapeResult:
    """Summary of a CoinGecko trending scrape cycle."""

    items_fetched: int = 0
    new_content_stored: int = 0
    duplicates_skipped: int = 0
    errors: list[str] = field(default_factory=list)


async def _ensure_coingecko_source(db: AsyncSession) -> DataSource:
    """Ensure a single DataSource exists for CoinGecko trending."""
    url = f"{settings.COINGECKO_BASE_URL}/search/trending"
    result = await db.execute(select(DataSource).where(DataSource.url == url))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    ds = DataSource(
        name="CoinGecko Trending",
        url=url,
        source_type="api",
        source_category="market_data",
        priority="high",
    )
    db.add(ds)
    await db.flush()
    logger.info("Registered new data source: CoinGecko Trending")
    await db.commit()
    return ds


def _build_coin_summary(coin: dict[str, Any]) -> tuple[str, str]:
    """Return (title, text_summary) for a trending coin entry."""
    item = coin.get("item", {}) or {}
    name = item.get("name") or "Unknown"
    symbol = item.get("symbol") or ""
    market_cap_rank = item.get("market_cap_rank")
    coingecko_rank = item.get("coingecko_rank")
    price_btc = item.get("price_btc")
    score = item.get("score")
    slug = item.get("id") or ""
    if slug:
        url = f"https://www.coingecko.com/en/coins/{slug}"
    else:
        url = "https://www.coingecko.com/"

    title = f"CoinGecko Trending — {name} ({symbol})".strip()

    parts: list[str] = []
    parts.append(f"{name} ({symbol}) is currently trending on CoinGecko.")
    if coingecko_rank is not None:
        parts.append(f"CoinGecko trending rank: {coingecko_rank}.")
    if market_cap_rank is not None:
        parts.append(f"Market cap rank: {market_cap_rank}.")
    if price_btc is not None:
        parts.append(f"Price (BTC): {price_btc}.")
    if score is not None:
        parts.append(f"Trending score: {score}.")
    parts.append(f"CoinGecko page: {url}")

    summary = clean_text(" ".join(str(p) for p in parts if p))
    return title, summary


async def run_coingecko_scrape_cycle(db: AsyncSession) -> CoinGeckoScrapeResult:
    """Fetch trending coins and store them as ScrapedContent."""
    result = CoinGeckoScrapeResult()

    ds = await _ensure_coingecko_source(db)

    # Basic guard: base URL must be configured
    base_url = settings.COINGECKO_BASE_URL.rstrip("/")
    endpoint = f"{base_url}/search/trending"

    headers: dict[str, str] = {
        "User-Agent": "SolanaNarrativeBot/1.0 (research; non-commercial)",
        "Accept": "application/json",
    }
    if settings.COINGECKO_API_KEY:
        headers["x-cg-pro-api-key"] = settings.COINGECKO_API_KEY

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
        try:
            resp = await client.get(endpoint, headers=headers)
            resp.raise_for_status()
        except Exception as e:
            msg = f"Failed to fetch CoinGecko trending: {e}"
            logger.error(msg)
            result.errors.append(msg)
            return result

        try:
            data = resp.json()
        except Exception as e:
            msg = f"Invalid JSON from CoinGecko trending endpoint: {e}"
            logger.error(msg)
            result.errors.append(msg)
            return result

        coins = data.get("coins") or []
        result.items_fetched = len(coins)

        for coin in coins:
            try:
                title, summary = _build_coin_summary(coin)
                if not summary or len(summary) < 40:
                    continue

                item = coin.get("item", {}) or {}
                slug = item.get("id") or ""
                if slug:
                    source_url = f"https://www.coingecko.com/en/coins/{slug}"
                else:
                    source_url = ds.url

                # Deduplicate by stable key: slug + score
                key = f"{slug}:{item.get('score')}"
                c_hash = content_hash(key or summary)

                existing = await db.execute(
                    select(ScrapedContent).where(
                        ScrapedContent.content_hash == c_hash,
                        ScrapedContent.data_source_id == ds.id,
                    )
                )
                if existing.scalar_one_or_none():
                    result.duplicates_skipped += 1
                    continue

                sc = ScrapedContent(
                    data_source_id=ds.id,
                    source_url=source_url,
                    title=title,
                    raw_content=truncate_text(summary),
                    content_hash=c_hash,
                    analysis_status="pending",
                    analysis_attempts=0,
                )
                db.add(sc)
                result.new_content_stored += 1
            except Exception as e:
                msg = f"Error processing CoinGecko coin entry: {e}"
                logger.error(msg)
                result.errors.append(msg)

        ds.last_scraped_at = utcnow()
        await db.commit()

    logger.info(
        "CoinGecko scrape complete: "
        f"{result.items_fetched} items, "
        f"{result.new_content_stored} new, "
        f"{result.duplicates_skipped} duplicates, "
        f"{len(result.errors)} errors"
    )
    return result

