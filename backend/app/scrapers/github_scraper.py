"""GitHub Solana repos scraper.

Uses the GitHub Search API to find recently-updated Solana-related repos,
fetches basic metadata (and optionally README snippets), and stores them
as ScrapedContent so they feed into Stage 1 → Stage 2.
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
class GithubScrapeResult:
    """Summary of a GitHub scraping cycle."""

    repos_fetched: int = 0
    new_content_stored: int = 0
    duplicates_skipped: int = 0
    errors: list[str] = field(default_factory=list)


SEARCH_QUERY = (
    "solana in:name,description,readme "
    "language:rust language:typescript language:javascript language:python"
)
MAX_REPOS_PER_RUN = 20


async def _ensure_github_source(db: AsyncSession) -> DataSource:
    """Ensure a single DataSource exists for GitHub Solana search."""
    url = f"{settings.GITHUB_BASE_URL}/search/repositories"
    result = await db.execute(select(DataSource).where(DataSource.url == url))
    existing = result.scalar_one_or_none()
    if existing:
        # Normalize the display name so sources show as just "GitHub".
        if existing.name != "GitHub":
            existing.name = "GitHub"
            await db.commit()
        return existing

    ds = DataSource(
        name="GitHub",
        url=url,
        source_type="github",
        source_category="developer",
        priority="high",
    )
    db.add(ds)
    await db.flush()
    logger.info("Registered new data source: GitHub Solana Search")
    await db.commit()
    return ds


def _build_repo_summary(repo: dict[str, Any], readme_snippet: str | None) -> tuple[str, str, str]:
    """Return (title, summary, key_for_hash) for a GitHub repo."""
    full_name = repo.get("full_name") or repo.get("name") or "unknown"
    description = repo.get("description") or ""
    stars = repo.get("stargazers_count")
    forks = repo.get("forks_count")
    issues = repo.get("open_issues_count")
    language = repo.get("language") or ""
    pushed_at = repo.get("pushed_at") or repo.get("updated_at") or ""
    html_url = repo.get("html_url") or ""
    topics = repo.get("topics") or []

    title = f"GitHub — {full_name} (recent Solana repo)"

    parts: list[str] = []
    parts.append(f"Repository: {full_name}.")
    if description:
        parts.append(f"Description: {description}.")
    if stars is not None:
        parts.append(f"Stars: {stars}.")
    if forks is not None:
        parts.append(f"Forks: {forks}.")
    if issues is not None:
        parts.append(f"Open issues: {issues}.")
    if language:
        parts.append(f"Primary language: {language}.")
    if pushed_at:
        parts.append(f"Last pushed at: {pushed_at}.")
    if topics:
        parts.append(f"Topics: {', '.join(topics)}.")

    # Highlight Solana relevance with a simple keyword check.
    solana_signals: list[str] = []
    text_blob = " ".join(
        [
            full_name.lower(),
            description.lower(),
            " ".join(topics).lower(),
            (readme_snippet or "").lower(),
        ]
    )
    if "solana" in text_blob:
        solana_signals.append("Mentions Solana explicitly.")
    if "anchor" in text_blob:
        solana_signals.append("Mentions Anchor framework.")
    if "program" in text_blob:
        solana_signals.append("Mentions on-chain programs.")
    if solana_signals:
        parts.append("Solana context: " + " ".join(solana_signals))

    if html_url:
        parts.append(f"GitHub URL: {html_url}.")

    if readme_snippet:
        parts.append("README snippet: " + readme_snippet)

    summary = clean_text(" ".join(str(p) for p in parts if p))
    key = f"{full_name}:{pushed_at}"
    return title, summary, key


async def _fetch_readme_snippet(
    client: httpx.AsyncClient, repo: dict[str, Any]
) -> str | None:
    """Fetch a small snippet of the README to enrich context (best-effort)."""
    readme_url = repo.get("url") or repo.get("repos_url")
    if not readme_url:
        return None

    # GitHub has a dedicated README endpoint: /repos/{owner}/{repo}/readme
    full_name = repo.get("full_name")
    if not full_name:
        return None
    readme_endpoint = f"{settings.GITHUB_BASE_URL}/repos/{full_name}/readme"

    headers: dict[str, str] = {"Accept": "application/vnd.github.v3.raw"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    try:
        resp = await client.get(readme_endpoint, headers=headers)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        text = resp.text or ""
        text = clean_text(text)
        if len(text) > 800:
            text = text[:800]
        return text
    except Exception as e:
        logger.warning(f"[GITHUB] Failed to fetch README for {full_name}: {e}")
        return None


async def run_github_scrape_cycle(db: AsyncSession) -> GithubScrapeResult:
    """
    Run a GitHub search for Solana repos and store summaries as ScrapedContent.

    Uses a single DataSource (GitHub Solana Search). Each repo becomes a
    ScrapedContent row keyed by full_name + pushed_at.
    """
    result = GithubScrapeResult()
    ds = await _ensure_github_source(db)

    headers: dict[str, str] = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "SolanaNarrativeBot/1.0 (research; non-commercial)",
    }
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
    else:
        logger.warning(
            "[GITHUB] GITHUB_TOKEN not configured — using unauthenticated requests (low rate limit)"
        )

    params = {
        "q": SEARCH_QUERY,
        "sort": "updated",
        "order": "desc",
        "per_page": MAX_REPOS_PER_RUN,
        "page": 1,
    }

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
        try:
            resp = await client.get(
                f"{settings.GITHUB_BASE_URL.rstrip('/')}/search/repositories",
                headers=headers,
                params=params,
            )
            resp.raise_for_status()
        except Exception as e:
            msg = f"Failed to search GitHub repos: {e}"
            logger.error(msg)
            result.errors.append(msg)
            return result

        try:
            data = resp.json()
        except Exception as e:
            msg = f"Invalid JSON from GitHub search: {e}"
            logger.error(msg)
            result.errors.append(msg)
            return result

        items = data.get("items") or []
        result.repos_fetched = len(items)

        for repo in items[:MAX_REPOS_PER_RUN]:
            try:
                readme_snippet = await _fetch_readme_snippet(client, repo)
                title, summary, key = _build_repo_summary(repo, readme_snippet)
                if not summary or len(summary) < 40:
                    continue

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

                html_url = repo.get("html_url") or ds.url
                sc = ScrapedContent(
                    data_source_id=ds.id,
                    source_url=html_url,
                    title=title,
                    raw_content=truncate_text(summary),
                    content_hash=c_hash,
                    analysis_status="pending",
                    analysis_attempts=0,
                )
                db.add(sc)
                result.new_content_stored += 1
            except Exception as e:
                msg = f"Error processing GitHub repo {repo.get('full_name')}: {e}"
                logger.error(msg)
                result.errors.append(msg)

        ds.last_scraped_at = utcnow()
        await db.commit()

    logger.info(
        "GitHub scrape complete: "
        f"{result.repos_fetched} repos, "
        f"{result.new_content_stored} new, "
        f"{result.duplicates_skipped} duplicates, "
        f"{len(result.errors)} errors"
    )
    return result

