"""Twitter/X scraper using ScrapeBatcher API.

Fetches latest tweets from verified Solana KOLs.
Rate limited to 5 requests/second (free tier).
"""

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.data_source import DataSource
from app.models.scraped_content import ScrapedContent
from app.scrapers.rate_limiter import scrapebatcher_limiter
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
                scrape_frequency="4h",
            )
            db.add(ds)
            await db.flush()
            source_map[username] = ds

    await db.commit()
    return source_map


async def run_twitter_scrape_cycle(db: AsyncSession) -> TwitterScrapeCycleResult:
    """
    Fetch latest tweet from each KOL via ScrapeBatcher API.

    Respects 5 req/sec rate limit using token bucket.
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

    logger.info(f"[TWITTER] Fetching latest tweets from {len(kols)} KOLs (rate limit: 5 req/sec)")

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
        # Process KOLs with rate limiting
        tweet_results: list[TweetResult | None] = []
        for idx, username in enumerate(kols):
            await scrapebatcher_limiter.acquire()
            logger.info(f"[TWITTER] [{idx + 1}/{len(kols)}] Fetching @{username}")
            try:
                tweet = await _fetch_kol_tweet(client, username)
                tweet_results.append(tweet)
                if tweet:
                    rt_tag = " [RT]" if tweet.is_retweet else ""
                    logger.info(
                        f"[TWITTER]   Got tweet{rt_tag} ({tweet.favorite_count} likes, "
                        f"{tweet.view_count or '?'} views): {tweet.full_text[:80]}..."
                    )
                else:
                    logger.info(f"[TWITTER]   No tweet data returned")
            except Exception as e:
                logger.error(f"[TWITTER]   FAILED @{username}: {e}")
                tweet_results.append(None)

        # Store results
        for tweet in tweet_results:
            if tweet is None:
                continue

            result.tweets_fetched += 1
            ds = source_map.get(tweet.username)
            if not ds:
                continue

            stored = await _store_tweet_if_new(db, ds, tweet)
            if stored:
                result.new_content_stored += 1
                logger.info(f"[TWITTER]   Stored new tweet from @{tweet.username}")
            else:
                result.duplicates_skipped += 1

            ds.last_scraped_at = utcnow()

        await db.commit()

    logger.info(
        f"Twitter scrape cycle complete: {result.tweets_fetched} fetched, "
        f"{result.new_content_stored} new, {result.duplicates_skipped} duplicates, "
        f"{len(result.errors)} errors"
    )
    return result


async def _fetch_kol_tweet(client: httpx.AsyncClient, username: str) -> TweetResult | None:
    """Fetch the latest tweet for a single KOL via ScrapeBadger.

    API returns {"data": [tweet1, tweet2, ...]} — an array of recent tweets.
    We pick the most recent original (non-retweet) tweet, falling back to the
    first tweet if all are retweets.
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
            return None

        # Prefer the most recent original tweet (non-retweet)
        tweet_data = None
        for t in tweets:
            if not t.get("is_retweet", False):
                tweet_data = t
                break

        # Fall back to the first tweet if all are retweets
        if tweet_data is None:
            tweet_data = tweets[0]

        tweet_id = str(tweet_data.get("id", ""))
        text = tweet_data.get("text", "")
        full_text = tweet_data.get("full_text", text)

        if not tweet_id or not full_text:
            logger.debug(f"No usable tweet data for @{username}")
            return None

        # Parse view_count (comes as string or None from API)
        raw_views = tweet_data.get("view_count")
        view_count = int(raw_views) if raw_views else None

        return TweetResult(
            username=tweet_data.get("username", username),
            user_name=tweet_data.get("user_name", username),
            tweet_id=tweet_id,
            text=text,
            full_text=clean_text(full_text),
            tweet_url=build_tweet_url(username, tweet_id),
            created_at=tweet_data.get("created_at"),
            lang=tweet_data.get("lang"),
            favorite_count=tweet_data.get("favorite_count", 0),
            retweet_count=tweet_data.get("retweet_count", 0),
            reply_count=tweet_data.get("reply_count", 0),
            quote_count=tweet_data.get("quote_count", 0),
            view_count=view_count,
            bookmark_count=tweet_data.get("bookmark_count", 0),
            is_retweet=tweet_data.get("is_retweet", False),
            is_quote_status=tweet_data.get("is_quote_status", False),
            user_mentions=[
                {"username": m.get("username", ""), "name": m.get("name", "")}
                for m in tweet_data.get("user_mentions", [])
            ],
            hashtags=tweet_data.get("hashtags", []),
            media=[
                {"type": m.get("type", ""), "url": m.get("url", "")}
                for m in tweet_data.get("media", [])
            ],
            urls=[
                {"url": u.get("expanded_url") or u.get("url", "")}
                for u in tweet_data.get("urls", [])
                if u.get("expanded_url") or u.get("url")
            ],
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            logger.warning(f"Rate limited fetching @{username} — will retry next cycle")
        else:
            logger.error(f"HTTP {e.response.status_code} fetching @{username}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching tweet for @{username}: {e}")
        return None


async def _store_tweet_if_new(
    db: AsyncSession, ds: DataSource, tweet: TweetResult
) -> bool:
    """Store tweet content if not duplicate. Returns True if stored."""
    c_hash = content_hash(tweet.full_text)

    existing = await db.execute(
        select(ScrapedContent).where(
            ScrapedContent.content_hash == c_hash,
            ScrapedContent.data_source_id == ds.id,
        )
    )
    if existing.scalar_one_or_none():
        return False

    # Build rich content for LLM analysis with engagement context
    mentions_str = ", ".join(
        f"@{m['username']}" for m in tweet.user_mentions
    ) if tweet.user_mentions else "none"

    media_str = ", ".join(
        f"{m['type']}: {m['url']}" for m in tweet.media
    ) if tweet.media else "none"

    view_str = f"{tweet.view_count:,}" if tweet.view_count else "N/A"

    content_text = (
        f"@{tweet.username} ({tweet.user_name}) tweeted:\n"
        f"{tweet.full_text}\n\n"
        f"--- Engagement ---\n"
        f"Likes: {tweet.favorite_count} | Retweets: {tweet.retweet_count} | "
        f"Replies: {tweet.reply_count} | Quotes: {tweet.quote_count} | "
        f"Views: {view_str} | Bookmarks: {tweet.bookmark_count}\n"
        f"Is retweet: {tweet.is_retweet} | Is quote: {tweet.is_quote_status}\n"
        f"Mentions: {mentions_str}\n"
        f"Media: {media_str}\n"
        f"Posted: {tweet.created_at or 'unknown'}\n"
        f"Tweet URL: {tweet.tweet_url}"
    )

    sc = ScrapedContent(
        data_source_id=ds.id,
        source_url=tweet.tweet_url,
        title=f"@{tweet.username} — {tweet.full_text[:80]}",
        raw_content=content_text,
        content_hash=c_hash,
    )
    db.add(sc)
    await db.flush()
    return True
