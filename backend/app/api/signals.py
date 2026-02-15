"""API endpoints for signals."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.data_source import DataSource
from app.models.scraped_content import ScrapedContent
from app.models.signal import Signal
from app.schemas.signal import SignalDetailResponse, SignalListResponse, SignalResponse

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("", response_model=SignalListResponse)
async def list_signals(
    q: str | None = Query(None, description="Search in title/description/evidence"),
    source_type: str | None = Query(None, description="Filter by data source type (web, twitter, etc.)"),
    data_source_id: int | None = Query(None, ge=1, description="Filter by specific data source id"),
    signal_type: str | None = Query(None, description="Filter by signal type (developer, social, etc.)"),
    novelty: str | None = Query(None, description="Filter by novelty (high, medium, low)"),
    tags: str | None = Query(None, description="Comma-separated tags; all must be present"),
    related_projects: str | None = Query(None, description="Comma-separated projects; all must be present"),
    start_date: datetime | None = Query(None, description="Filter signals created_at >= start_date (ISO-8601)"),
    end_date: datetime | None = Query(None, description="Filter signals created_at <= end_date (ISO-8601)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List signals with optional filtering and pagination (newest first)."""

    query = (
        select(Signal, ScrapedContent, DataSource)
        .join(ScrapedContent, Signal.scraped_content_id == ScrapedContent.id)
        .join(DataSource, ScrapedContent.data_source_id == DataSource.id)
    )

    if q:
        like = f"%{q.strip()}%"
        query = query.where(
            or_(
                Signal.signal_title.ilike(like),
                Signal.description.ilike(like),
                Signal.evidence.ilike(like),
            )
        )

    if source_type:
        query = query.where(DataSource.source_type == source_type)

    if data_source_id is not None:
        query = query.where(DataSource.id == data_source_id)

    if signal_type:
        query = query.where(Signal.signal_type == signal_type)

    if novelty:
        query = query.where(Signal.novelty == novelty)

    if start_date:
        query = query.where(Signal.created_at >= start_date)

    if end_date:
        query = query.where(Signal.created_at <= end_date)

    # Tag filtering (JSON contains) — require all provided tags
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        for tag in tag_list:
            query = query.where(Signal.tags.contains([tag]))

    # Project filtering (JSON contains) — require all provided projects
    if related_projects:
        proj_list = [p.strip() for p in related_projects.split(",") if p.strip()]
        for proj in proj_list:
            query = query.where(Signal.related_projects.contains([proj]))

    # Count total before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Sort and paginate
    query = query.order_by(Signal.created_at.desc(), Signal.id.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    rows = result.all()

    return SignalListResponse(
        signals=[
            SignalResponse(
                id=s.id,
                scraped_content_id=s.scraped_content_id,
                signal_title=s.signal_title,
                description=s.description,
                signal_type=s.signal_type,
                novelty=s.novelty,
                evidence=s.evidence,
                related_projects=s.related_projects or [],
                tags=s.tags or [],
                created_at=s.created_at,
                content_url=c.source_url,
                content_title=c.title,
                scraped_at=c.scraped_at,
                data_source_id=ds.id,
                data_source_name=ds.name,
                data_source_url=ds.url,
                data_source_type=ds.source_type,
                data_source_category=ds.source_category,
            )
            for (s, c, ds) in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{signal_id}", response_model=SignalDetailResponse)
async def get_signal(
    signal_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single signal with its source URL and data source metadata."""

    result = await db.execute(
        select(Signal, ScrapedContent, DataSource)
        .join(ScrapedContent, Signal.scraped_content_id == ScrapedContent.id)
        .join(DataSource, ScrapedContent.data_source_id == DataSource.id)
        .where(Signal.id == signal_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Signal not found")

    s, c, ds = row
    return SignalDetailResponse(
        id=s.id,
        scraped_content_id=s.scraped_content_id,
        signal_title=s.signal_title,
        description=s.description,
        signal_type=s.signal_type,
        novelty=s.novelty,
        evidence=s.evidence,
        related_projects=s.related_projects or [],
        tags=s.tags or [],
        created_at=s.created_at,
        content_url=c.source_url,
        content_title=c.title,
        scraped_at=c.scraped_at,
        data_source_id=ds.id,
        data_source_name=ds.name,
        data_source_url=ds.url,
        data_source_type=ds.source_type,
        data_source_category=ds.source_category,
    )

