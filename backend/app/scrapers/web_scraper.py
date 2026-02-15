"""Web scraper for Solana ecosystem data sources.

Handles HTML pages, Reddit JSON feeds, and PDF downloads.
Supports deep link following to depth 2 for blog index pages.
"""

import asyncio
import io
import time
from dataclasses import dataclass, field

import httpx
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.data_source import DataSource
from app.models.scraped_content import ScrapedContent
from app.scrapers.url_resolver import (
    extract_article_links,
    extract_main_content,
    extract_title,
)
from app.utils.helpers import content_hash, clean_text, truncate_text, utcnow
from app.utils.logger import logger

settings = get_settings()

# Source definitions — each maps to a DataSource row
WEB_SOURCES = [
    {
        "name": "Solana News",
        "url": "https://solana.com/news",
        "source_type": "web",
        "source_category": "ecosystem_news",
        "priority": "high",
        "deep_link": True,
    },
    {
        "name": "Helius Blog",
        "url": "https://www.helius.dev/blog",
        "source_type": "web",
        "source_category": "developer_blog",
        "priority": "high",
        "deep_link": True,
    },
    {
        "name": "Solana Mobile Blog",
        "url": "https://blog.solanamobile.com/",
        "source_type": "web",
        "source_category": "mobile",
        "priority": "high",
        "deep_link": True,
    },
    {
        "name": "Reddit r/solana",
        "url": "https://www.reddit.com/r/solana.json?limit=50",
        "source_type": "reddit",
        "source_category": "community_forum",
        "priority": "high",
        "deep_link": False,
    },
    {
        "name": "Reddit Solana Search",
        "url": "https://www.reddit.com/search.json?q=solana&limit=50",
        "source_type": "reddit",
        "source_category": "community_forum",
        "priority": "medium",
        "deep_link": False,
    },
    {
        "name": "Solana Homepage",
        "url": "https://solana.com/",
        "source_type": "web",
        "source_category": "ecosystem_news",
        "priority": "medium",
        "deep_link": False,
    },
    {
        "name": "Solana Compass",
        "url": "https://solanacompass.com/",
        "source_type": "web",
        "source_category": "ecosystem_news",
        "priority": "medium",
        "deep_link": False,
    },
    {
        "name": "Arkham Research",
        "url": "https://info.arkm.com/research",
        "source_type": "web",
        "source_category": "research",
        "priority": "low",
        "deep_link": True,
    },
    {
        "name": "Electric Capital",
        "url": "https://www.electriccapital.com/",
        "source_type": "web",
        "source_category": "research",
        "priority": "low",
        "deep_link": True,
    },
    {
        "name": "CoinGecko 2025 Report",
        "url": "https://assets.coingecko.com/reports/2025/CoinGecko-2025-Annual-Crypto-Industry-Report.pdf",
        "source_type": "pdf",
        "source_category": "research",
        "priority": "low",
        "deep_link": False,
    },
]

HEADERS = {
    "User-Agent": "SolanaNarrativeBot/1.0 (research; non-commercial)",
    "Accept": "text/html,application/xhtml+xml,application/json,application/pdf",
}


@dataclass
class ScrapeResult:
    """Result of scraping a single URL."""
    source_url: str
    title: str | None
    content: str
    content_hash: str
    is_duplicate: bool = False


@dataclass
class WebScrapeCycleResult:
    """Summary of a full web scraping cycle."""
    total_sources: int = 0
    total_pages_fetched: int = 0
    new_content_stored: int = 0
    duplicates_skipped: int = 0
    errors: list[str] = field(default_factory=list)


async def ensure_web_sources_exist(db: AsyncSession) -> dict[str, DataSource]:
    """Ensure all web source definitions exist in the database. Return map of url -> DataSource."""
    source_map: dict[str, DataSource] = {}

    for src in WEB_SOURCES:
        result = await db.execute(select(DataSource).where(DataSource.url == src["url"]))
        existing = result.scalar_one_or_none()

        if existing:
            source_map[src["url"]] = existing
        else:
            ds = DataSource(
                name=src["name"],
                url=src["url"],
                source_type=src["source_type"],
                source_category=src["source_category"],
                priority=src["priority"],
            )
            db.add(ds)
            await db.flush()
            source_map[src["url"]] = ds
            logger.info(f"Registered new data source: {src['name']}")

    await db.commit()
    return source_map


async def run_web_scrape_cycle(db: AsyncSession) -> WebScrapeCycleResult:
    """
    Execute a full web scraping cycle for all configured sources.

    Steps:
    1. Ensure all sources are registered in DB
    2. For each source, fetch content (HTML/JSON/PDF)
    3. For deep-link sources, follow article links to depth 2
    4. Deduplicate by content hash
    5. Store new content in scraped_content table
    """
    result = WebScrapeCycleResult()
    source_map = await ensure_web_sources_exist(db)
    result.total_sources = len(source_map)

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=settings.REQUEST_TIMEOUT,
        follow_redirects=True,
    ) as client:
        for src_idx, src_def in enumerate(WEB_SOURCES):
            ds = source_map[src_def["url"]]
            if not ds.is_active:
                logger.info(f"[WEB] Skipping inactive source: {ds.name}")
                continue

            try:
                logger.info(f"[WEB] [{src_idx + 1}/{len(WEB_SOURCES)}] Scraping: {ds.name}")
                logger.info(f"[WEB]   URL: {ds.url}")
                logger.info(f"[WEB]   Type: {src_def['source_type']} | Priority: {src_def['priority']} | Deep link: {src_def.get('deep_link', False)}")

                if src_def["source_type"] == "pdf":
                    scrape_results = await _scrape_pdf(client, ds)
                elif src_def["source_type"] == "reddit":
                    scrape_results = await _scrape_reddit(client, ds)
                else:
                    scrape_results = await _scrape_html(
                        client, ds, deep_link=src_def.get("deep_link", False)
                    )

                # Store results
                new_for_source = 0
                dupes_for_source = 0
                for sr in scrape_results:
                    result.total_pages_fetched += 1
                    stored = await _store_if_new(db, ds, sr)
                    if stored:
                        result.new_content_stored += 1
                        new_for_source += 1
                    else:
                        result.duplicates_skipped += 1
                        dupes_for_source += 1

                logger.info(
                    f"[WEB]   Done: {len(scrape_results)} pages fetched, "
                    f"{new_for_source} new, {dupes_for_source} duplicates"
                )

                # Update last_scraped_at
                ds.last_scraped_at = utcnow()
                await db.commit()

                # Respectful delay between domains
                await asyncio.sleep(settings.SCRAPE_DELAY_SECONDS)

            except Exception as e:
                error_msg = f"Error scraping {ds.name}: {e}"
                logger.error(f"[WEB]   FAILED: {error_msg}")
                result.errors.append(error_msg)
                continue

    logger.info(
        f"Web scrape cycle complete: {result.new_content_stored} new, "
        f"{result.duplicates_skipped} duplicates, {len(result.errors)} errors"
    )
    return result


async def _scrape_html(
    client: httpx.AsyncClient, ds: DataSource, deep_link: bool = False
) -> list[ScrapeResult]:
    """Scrape an HTML page. If deep_link=True, follow article links to depth 2."""
    results: list[ScrapeResult] = []

    resp = await _fetch_with_retry(client, ds.url)
    if resp is None:
        return results

    html = resp.text
    title = extract_title(html)
    main_content = extract_main_content(html)

    if main_content and len(main_content.strip()) > 50:
        results.append(ScrapeResult(
            source_url=ds.url,
            title=title,
            content=truncate_text(clean_text(main_content)),
            content_hash=content_hash(main_content),
        ))

    # Follow deep links (depth 2)
    if deep_link:
        article_links = extract_article_links(html, ds.url)
        logger.info(f"  Found {len(article_links)} deep links on {ds.name}")

        for link in article_links[:20]:  # Cap at 20 links per source
            await asyncio.sleep(settings.SCRAPE_DELAY_SECONDS)
            try:
                resp2 = await _fetch_with_retry(client, link)
                if resp2 is None:
                    continue
                html2 = resp2.text
                article_title = extract_title(html2)
                article_content = extract_main_content(html2)

                if article_content and len(article_content.strip()) > 100:
                    results.append(ScrapeResult(
                        source_url=link,
                        title=article_title,
                        content=truncate_text(clean_text(article_content)),
                        content_hash=content_hash(article_content),
                    ))
            except Exception as e:
                logger.warning(f"  Failed to fetch deep link {link}: {e}")

    return results


async def _scrape_reddit(client: httpx.AsyncClient, ds: DataSource) -> list[ScrapeResult]:
    """Scrape Reddit JSON feeds and extract post data."""
    results: list[ScrapeResult] = []

    resp = await _fetch_with_retry(client, ds.url)
    if resp is None:
        return results

    try:
        data = resp.json()
        posts = data.get("data", {}).get("children", [])

        for post in posts:
            post_data = post.get("data", {})
            title = post_data.get("title", "")
            selftext = post_data.get("selftext", "")
            score = post_data.get("score", 0)
            num_comments = post_data.get("num_comments", 0)
            permalink = post_data.get("permalink", "")
            subreddit = post_data.get("subreddit", "")

            full_url = f"https://www.reddit.com{permalink}" if permalink else ds.url
            content = (
                f"[r/{subreddit}] {title}\n"
                f"Score: {score} | Comments: {num_comments}\n\n"
                f"{selftext}"
            )

            if content.strip():
                results.append(ScrapeResult(
                    source_url=full_url,
                    title=title,
                    content=truncate_text(clean_text(content)),
                    content_hash=content_hash(content),
                ))
    except Exception as e:
        logger.error(f"Failed to parse Reddit JSON from {ds.url}: {e}")

    return results


async def _scrape_pdf(client: httpx.AsyncClient, ds: DataSource) -> list[ScrapeResult]:
    """Download and extract text from a PDF file."""
    results: list[ScrapeResult] = []

    resp = await _fetch_with_retry(client, ds.url)
    if resp is None:
        return results

    try:
        reader = PdfReader(io.BytesIO(resp.content))
        text_parts: list[str] = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            # Only keep pages mentioning Solana for efficiency
            if "solana" in page_text.lower():
                text_parts.append(page_text)

        if text_parts:
            full_text = "\n\n".join(text_parts)
            results.append(ScrapeResult(
                source_url=ds.url,
                title=f"CoinGecko Report - Solana Sections",
                content=truncate_text(clean_text(full_text)),
                content_hash=content_hash(full_text),
            ))
    except Exception as e:
        logger.error(f"Failed to parse PDF from {ds.url}: {e}")

    return results


async def _fetch_with_retry(
    client: httpx.AsyncClient, url: str, max_retries: int = 3
) -> httpx.Response | None:
    """Fetch a URL with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                wait = 2 ** (attempt + 1)
                logger.warning(f"Rate limited on {url}, waiting {wait}s (attempt {attempt + 1})")
                await asyncio.sleep(wait)
            elif e.response.status_code >= 500:
                wait = 2 ** attempt
                logger.warning(f"Server error {e.response.status_code} on {url}, retrying in {wait}s")
                await asyncio.sleep(wait)
            else:
                logger.error(f"HTTP {e.response.status_code} on {url}: {e}")
                return None
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            wait = 2 ** attempt
            logger.warning(f"Connection error on {url}: {e}, retrying in {wait}s")
            await asyncio.sleep(wait)
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    logger.error(f"All {max_retries} retries exhausted for {url}")
    return None


async def _store_if_new(db: AsyncSession, ds: DataSource, sr: ScrapeResult) -> bool:
    """Store scraped content if it's not a duplicate. Returns True if stored."""
    existing = await db.execute(
        select(ScrapedContent).where(
            ScrapedContent.content_hash == sr.content_hash,
            ScrapedContent.data_source_id == ds.id,
        )
    )
    if existing.scalar_one_or_none():
        return False

    sc = ScrapedContent(
        data_source_id=ds.id,
        source_url=sr.source_url,
        title=sr.title,
        raw_content=sr.content,
        content_hash=sr.content_hash,
        analysis_status="pending",
        analysis_attempts=0,
    )
    db.add(sc)
    await db.flush()
    return True
