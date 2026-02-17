"""Dune Analytics scraper for on-chain trending analyses.

Executes one or more configured Dune queries using the async job model,
waits for completion, then stores result rows as ScrapedContent so they
can flow through Stage 1 → Stage 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import asyncio
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
class DuneQueryConfig:
    name: str
    query_id: int
    description: str | None = None


@dataclass
class DuneScrapeResult:
    """Summary of a Dune scraping cycle."""

    queries_executed: int = 0
    rows_processed: int = 0
    new_content_stored: int = 0
    duplicates_skipped: int = 0
    errors: list[str] = field(default_factory=list)


# NOTE: You should replace these placeholder IDs with your actual Dune query IDs.
DUNE_QUERIES: list[DuneQueryConfig] = [
    DuneQueryConfig(
        name="Dune — Trending Programs",
        query_id=0,
        description="Top Solana programs by recent tx volume / activity.",
    ),
]


async def _ensure_dune_source(db: AsyncSession, cfg: DuneQueryConfig) -> DataSource:
    """Ensure a DataSource exists for a given Dune query."""
    url = f"{settings.DUNE_BASE_URL}/query/{cfg.query_id}"
    result = await db.execute(select(DataSource).where(DataSource.url == url))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    ds = DataSource(
        name=cfg.name,
        url=url,
        source_type="dune",
        source_category="onchain",
        priority="high",
    )
    db.add(ds)
    await db.flush()
    logger.info(f"Registered new data source: {cfg.name} (Dune query {cfg.query_id})")
    await db.commit()
    return ds


async def _execute_dune_query(
    client: httpx.AsyncClient, cfg: DuneQueryConfig
) -> tuple[str | None, list[dict[str, Any]]]:
    """Execute a single Dune query and return (error, rows)."""
    if not settings.DUNE_API_KEY:
        return ("DUNE_API_KEY not configured — skipping Dune queries", [])

    base = settings.DUNE_BASE_URL.rstrip("/")
    headers = {
        "x-dune-api-key": settings.DUNE_API_KEY,
        "Accept": "application/json",
    }

    try:
        # 1) Start execution
        start_resp = await client.post(f"{base}/query/{cfg.query_id}/execute", headers=headers)
        start_resp.raise_for_status()
        start_data = start_resp.json()
        execution_id = start_data.get("execution_id") or start_data.get("executionId")
        if not execution_id:
            return (f"No execution_id returned for Dune query {cfg.query_id}", [])

        # 2) Poll for completion
        status_url = f"{base}/execution/{execution_id}/status"
        results_url = f"{base}/execution/{execution_id}/results"
        max_wait_seconds = 60
        interval = 3
        waited = 0
        while waited < max_wait_seconds:
            status_resp = await client.get(status_url, headers=headers)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            state = (status_data.get("state") or status_data.get("status") or "").upper()
            if state in {"COMPLETED", "SUCCESS"}:
                break
            if state in {"FAILED", "ERROR", "CANCELLED"}:
                return (f"Dune execution {execution_id} failed with state={state}", [])
            await asyncio.sleep(interval)
            waited += interval
        else:
            return (f"Dune execution {execution_id} timed out after {max_wait_seconds}s", [])

        # 3) Fetch results
        res_resp = await client.get(results_url, headers=headers)
        res_resp.raise_for_status()
        res_data = res_resp.json()
        # Recent Dune API shape: {"result": {"rows": [...]}}
        result_obj = res_data.get("result") or res_data
        rows = result_obj.get("rows") or result_obj.get("data") or []
        if not isinstance(rows, list):
            return (f"Unexpected results format for execution {execution_id}", [])
        return (None, rows)

    except Exception as e:
        return (f"Error executing Dune query {cfg.query_id}: {e}", [])


def _build_row_summary(cfg: DuneQueryConfig, row: dict[str, Any]) -> tuple[str, str, str]:
    """Return (title, summary, key_for_hash) for a Dune result row."""
    # Attempt to pull common fields but keep generic.
    program = row.get("program") or row.get("program_name") or row.get("address") or ""
    label = row.get("label") or row.get("name") or ""
    tx_count = row.get("tx_count") or row.get("transactions") or row.get("count")
    volume = row.get("volume") or row.get("volume_usd") or row.get("volume_sol")
    unique_users = row.get("unique_users") or row.get("unique_wallets")
    timespan = row.get("timespan") or row.get("window") or ""

    identifier = label or program or "Unknown entity"
    title = f"{cfg.name} — {identifier}"

    parts: list[str] = []
    parts.append(f"{identifier} appears in Dune query '{cfg.name}', indicating on-chain activity.")
    if timespan:
        parts.append(f"Time window: {timespan}.")
    if tx_count is not None:
        parts.append(f"Transactions: {tx_count}.")
    if volume is not None:
        parts.append(f"Volume: {volume}.")
    if unique_users is not None:
        parts.append(f"Unique users/wallets: {unique_users}.")

    # Append a compact key=value summary of all columns for the LLM.
    kv_pairs = ", ".join(f"{k}={v}" for k, v in row.items())
    parts.append(f"Raw metrics: {kv_pairs}.")

    summary = clean_text(" ".join(str(p) for p in parts if p))

    # Use a stable key for deduplication: program/address + timespan (if present)
    key = f"{cfg.query_id}:{program or label}:{timespan}"
    return title, summary, key


async def run_dune_scrape_cycle(db: AsyncSession) -> DuneScrapeResult:
    """
    Execute configured Dune queries and store their rows as ScrapedContent.

    Each query becomes a DataSource, and each result row becomes a content row.
    """
    result = DuneScrapeResult()

    if not settings.DUNE_API_KEY:
        msg = "DUNE_API_KEY not configured — skipping Dune scrape cycle"
        logger.warning(msg)
        result.errors.append(msg)
        return result

    base = settings.DUNE_BASE_URL.rstrip("/")
    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
        for cfg in DUNE_QUERIES:
            if not cfg.query_id:
                # Placeholder entry left at 0 — skip until configured.
                logger.info(f"[DUNE] Skipping placeholder query config: {cfg.name}")
                continue

            ds = await _ensure_dune_source(db, cfg)
            logger.info(f"[DUNE] Executing query {cfg.query_id} ({cfg.name}) at {base}")

            err, rows = await _execute_dune_query(client, cfg)
            if err:
                logger.error(err)
                result.errors.append(err)
                continue

            result.queries_executed += 1
            result.rows_processed += len(rows)

            for row in rows:
                try:
                    title, summary, key = _build_row_summary(cfg, row)
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

                    # Prefer a Solana explorer link if present; otherwise use the DataSource URL.
                    explorer_url = row.get("explorer_url") or row.get("program_url")
                    source_url = explorer_url or ds.url

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
                    msg = f"Error processing Dune row for query {cfg.query_id}: {e}"
                    logger.error(msg)
                    result.errors.append(msg)

            ds.last_scraped_at = utcnow()
            await db.commit()

    logger.info(
        "Dune scrape complete: "
        f"{result.queries_executed} queries, "
        f"{result.rows_processed} rows, "
        f"{result.new_content_stored} new, "
        f"{result.duplicates_skipped} duplicates, "
        f"{len(result.errors)} errors"
    )
    return result

