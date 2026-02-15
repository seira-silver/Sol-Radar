"""Twitter/X scraper using ScrapeBatcher API.

Fetches latest tweets from verified Solana KOLs.
Rate limited to 5 requests/second (free tier).
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.data_source import DataSource
from app.models.scraped_content import ScrapedContent
from app.scrapers.rate_limiter import scrapebadger_limiter
from app.utils.helpers import build_tweet_url, content_hash, clean_text, utcnow
from app.utils.logger import logger

settings = get_settings()

SCRAPEBATCHER_BASE = "https://scrapebadger.com"
KOLS_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "verified_solana_kols.json"


@dataclass
class TweetResult:
    username: str
    user_name: str  # display name
    tweet_id: str
    text: str
    full_text: str
    tweet_url: str
    # Full tweet payload from the API (see data/tweets_demo.json)
    raw: dict = field(default_factory=dict)
    created_at: str | None = None
    lang: str | None = None
    # Engagement metrics
    favorite_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    view_count: int | None = None
    bookmark_count: int = 0
    # Tweet metadata
    is_retweet: bool = False
    is_quote_status: bool = False
    # Entities
    user_mentions: list[dict] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    media: list[dict] = field(default_factory=list)
    urls: list[dict] = field(default_factory=list)


@dataclass
class TwitterScrapeCycleResult:
    total_kols: int = 0
    tweets_fetched: int = 0
    new_content_stored: int = 0
    duplicates_skipped: int = 0
    # Stage 1 is run at the job level (always before Stage 2)
    # so we don't accidentally run Stage 2 without fresh signals.
    signals_extracted: int = 0
    new_content_ids: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def load_kols() -> list[str]:
    """Load KOL handles from the verified_solana_kols.json file."""
    try:
        with open(KOLS_FILE, "r") as f:
            kols = json.load(f)
        # Strip @ prefix
        return [k.lstrip("@") for k in kols]
    except FileNotFoundError:
        logger.error(f"KOLs file not found: {KOLS_FILE}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in KOLs file: {KOLS_FILE}")
        return []


async def ensure_twitter_sources_exist(
    db: AsyncSession, kols: list[str]
) -> dict[str, DataSource]:
    """Ensure each KOL has a DataSource entry. Return map of username -> DataSource."""
    source_map: dict[str, DataSource] = {}

    for username in kols:
        url = f"https://x.com/{username}"
        result = await db.execute(select(DataSource).where(DataSource.url == url))
        existing = result.scalar_one_or_none()

        if existing:
            source_map[username] = existing
        else:
            ds = DataSource(
                name=f"@{username}",
                url=url,
                source_type="twitter",
                source_category="social_kol",
                priority="high",
            )
            db.add(ds)
            await db.flush()
            source_map[username] = ds

    await db.commit()
    return source_map


async def run_twitter_scrape_cycle(db: AsyncSession) -> TwitterScrapeCycleResult:
    """
    Fetch latest tweet from each KOL via ScrapeBadger API.

    Per-KOL flow: fetch tweets → store any new tweets as ScrapedContent (pending).
    Stage 1 analysis is intentionally NOT run here; it is executed by the
    scheduled job right before Stage 2 synthesis to guarantee ordering:
      Stage 1 (signals) → Stage 2 (narratives).
    Respects ScrapeBadger RPM rate limit (configurable via SCRAPEBADGER_RPM).
    """
    result = TwitterScrapeCycleResult()
    kols = load_kols()
    result.total_kols = len(kols)

    if not kols:
        logger.warning("No KOLs loaded — skipping Twitter scrape")
        return result

    if not settings.SCRAPEBADGER_API_KEY:
        logger.error("SCRAPEBADGER_API_KEY not configured — skipping Twitter scrape")
        return result

    source_map = await ensure_twitter_sources_exist(db, kols)

    logger.info(
        f"[TWITTER] Fetching latest tweets from {len(kols)} KOLs "
        f"(rate limit: {settings.SCRAPEBADGER_RPM} req/min)"
    )

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
        for idx, username in enumerate(kols):
            # ── Rate limit before each API call ──
            await scrapebadger_limiter.acquire()
            logger.info(f"[TWITTER] [{idx + 1}/{len(kols)}] Fetching @{username}")

            try:
                tweets = await _fetch_kol_tweets(
                    client, username, limit=settings.TWITTER_TWEETS_PER_KOL
                )
            except Exception as e:
                logger.error(f"[TWITTER]   FAILED @{username}: {e}")
                result.errors.append(f"@{username}: {e}")
                continue

            if not tweets:
                logger.info(f"[TWITTER]   No tweet data returned")
                continue

            result.tweets_fetched += len(tweets)
            ds = source_map.get(username)
            if not ds:
                continue

            # ── Store tweets (each tweet is its own ScrapedContent) ──
            stored_any = False
            for t in tweets:
                rt_tag = " [RT]" if t.is_retweet else ""
                logger.info(
                    f"[TWITTER]   Got tweet{rt_tag} ({t.favorite_count} likes, "
                    f"{t.view_count or '?'} views): {t.full_text[:80]}..."
                )

                stored_content = await _store_tweet_if_new(db, ds, t)
                if stored_content is None:
                    result.duplicates_skipped += 1
                    continue

                stored_any = True
                result.new_content_stored += 1
                result.new_content_ids.append(stored_content.id)

            if not stored_any:
                continue

            ds.last_scraped_at = utcnow()
            await db.commit()

    logger.info(
        f"Twitter scrape cycle complete: {result.tweets_fetched} fetched, "
        f"{result.new_content_stored} new, {result.duplicates_skipped} duplicates, "
        f"{result.signals_extracted} signals, {len(result.errors)} errors"
    )
    return result


async def _fetch_kol_tweets(
    client: httpx.AsyncClient, username: str, limit: int = 1
) -> list[TweetResult]:
    """Fetch the latest tweets for a single KOL via ScrapeBadger.

    API returns {"data": [tweet1, tweet2, ...]} — an array of recent tweets.
    We prefer original (non-retweet) tweets; if none exist we fall back to
    retweets. Returns up to `limit` items.
    """
    try:
        resp = await client.get(
            f"{SCRAPEBATCHER_BASE}/v1/twitter/users/{username}/latest_tweets",
            headers={
                "x-api-key": settings.SCRAPEBADGER_API_KEY,
            },
        )
        resp.raise_for_status()
        data = resp.json()

        # Response shape: {"data": [...], "next_cursor": "..."}
        tweets = data.get("data", [])

        if not tweets:
            logger.debug(f"No tweets returned for @{username}")
            return []

        # Prefer original tweets, then fill with retweets if needed
        originals = [t for t in tweets if not t.get("is_retweet", False)]
        ordered = originals + [t for t in tweets if t.get("is_retweet", False)]

        out: list[TweetResult] = []
        seen_ids: set[str] = set()
        for t in ordered:
            if len(out) >= max(1, limit):
                break

            tweet_id = str(t.get("id", ""))
            if not tweet_id or tweet_id in seen_ids:
                continue

            text = t.get("text", "")
            full_text = t.get("full_text", text)
            if not full_text:
                continue

            # Parse view_count (comes as string or None from API)
            raw_views = t.get("view_count")
            view_count = int(raw_views) if raw_views else None

            # Keep the API payload shape as-is (see data/tweets_demo.json),
            # but we also attach a cleaned version of full_text for analysis use.
            raw_payload = dict(t)
            raw_payload["full_text"] = full_text

            out.append(
                TweetResult(
                    username=t.get("username", username),
                    user_name=t.get("user_name", username),
                    tweet_id=tweet_id,
                    text=text,
                    full_text=clean_text(full_text),
                    tweet_url=build_tweet_url(username, tweet_id),
                    raw=raw_payload,
                    created_at=t.get("created_at"),
                    lang=t.get("lang"),
                    favorite_count=t.get("favorite_count", 0),
                    retweet_count=t.get("retweet_count", 0),
                    reply_count=t.get("reply_count", 0),
                    quote_count=t.get("quote_count", 0),
                    view_count=view_count,
                    bookmark_count=t.get("bookmark_count", 0),
                    is_retweet=t.get("is_retweet", False),
                    is_quote_status=t.get("is_quote_status", False),
                    user_mentions=[
                        {"username": m.get("username", ""), "name": m.get("name", "")}
                        for m in t.get("user_mentions", [])
                    ],
                    hashtags=t.get("hashtags", []),
                    media=[
                        {"type": m.get("type", ""), "url": m.get("url", "")}
                        for m in t.get("media", [])
                    ],
                    urls=[
                        {"url": u.get("expanded_url") or u.get("url", "")}
                        for u in t.get("urls", [])
                        if u.get("expanded_url") or u.get("url")
                    ],
                )
            )
            seen_ids.add(tweet_id)

        return out

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            logger.warning(f"Rate limited fetching @{username} — will retry next cycle")
        else:
            logger.error(f"HTTP {e.response.status_code} fetching @{username}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching tweet for @{username}: {e}")
        return []


async def _store_tweet_if_new(
    db: AsyncSession, ds: DataSource, tweet: TweetResult
) -> ScrapedContent | None:
    """Store tweet content if not duplicate. Returns ScrapedContent if stored, None if duplicate."""
    # Dedupe by tweet URL/id (edits shouldn't create new rows + re-analysis).
    c_hash = content_hash(tweet.tweet_url)

    existing = await db.execute(
        select(ScrapedContent).where(
            ScrapedContent.content_hash == c_hash,
            ScrapedContent.data_source_id == ds.id,
        )
    )
    if existing.scalar_one_or_none():
        return None

    # Store tweet in the same JSON shape as the API (see data/tweets_demo.json).
    # This makes downstream parsing consistent and preserves fields we may use later.
    content_text = json.dumps(tweet.raw or {}, ensure_ascii=False, indent=2)

    sc = ScrapedContent(
        data_source_id=ds.id,
        source_url=tweet.tweet_url,
        title=f"@{tweet.username} — {tweet.full_text[:80]}",
        raw_content=content_text,
        content_hash=c_hash,
        analysis_status="pending",
        analysis_attempts=0,
    )
    db.add(sc)
    await db.flush()
    return sc
