"""API endpoints for narratives."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.narrative import Narrative, NarrativeSource
from app.models.narrative_signal_link import NarrativeSignalLink
from app.models.idea import Idea
from app.models.data_source import DataSource
from app.models.signal import Signal
from app.models.scraped_content import ScrapedContent
from app.schemas.narrative import (
    NarrativeResponse,
    NarrativeListResponse,
    NarrativeDetailResponse,
    IdeaInNarrative,
    NarrativeSourceResponse,
    SupportingSignalResponse,
)

router = APIRouter(prefix="/narratives", tags=["narratives"])


@router.get("", response_model=NarrativeListResponse)
async def list_narratives(
    is_active: bool | None = Query(None, description="Filter by active status"),
    min_confidence: str | None = Query(None, description="Minimum confidence: high, medium, low"),
    tags: str | None = Query(None, description="Comma-separated tags to filter by"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List narratives with filtering, sorting by velocity score."""
    query = select(Narrative)

    # Filters
    if is_active is not None:
        query = query.where(Narrative.is_active == is_active)

    if min_confidence:
        confidence_levels = {"high": ["high"], "medium": ["high", "medium"], "low": ["high", "medium", "low"]}
        allowed = confidence_levels.get(min_confidence, ["high", "medium", "low"])
        query = query.where(Narrative.confidence.in_(allowed))

    # Tag filtering (JSON contains)
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        for tag in tag_list:
            query = query.where(Narrative.tags.contains([tag]))

    # Count total before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Sort and paginate
    query = query.order_by(Narrative.velocity_score.desc(), Narrative.created_at.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query.options(selectinload(Narrative.ideas)))
    narratives = result.scalars().all()

    return NarrativeListResponse(
        narratives=[
            NarrativeResponse(
                id=n.id,
                title=n.title,
                summary=n.summary,
                confidence=n.confidence,
                confidence_reasoning=n.confidence_reasoning,
                is_active=n.is_active,
                velocity_score=n.velocity_score,
                rank=n.rank,
                tags=n.tags or [],
                key_evidence=n.key_evidence or [],
                supporting_source_names=n.supporting_source_names or [],
                idea_count=len(n.ideas) if n.ideas else 0,
                created_at=n.created_at,
                updated_at=n.updated_at,
                last_detected_at=n.last_detected_at,
            )
            for n in narratives
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/hackathons", response_model=NarrativeListResponse)
async def list_hackathon_narratives(
    is_active: bool | None = Query(None, description="Filter by active status"),
    min_confidence: str | None = Query(None, description="Minimum confidence: high, medium, low"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List narratives tagged with 'hackathon', sorted by velocity score."""
    query = select(Narrative).where(Narrative.tags.contains(["hackathon"]))

    # Filters
    if is_active is not None:
        query = query.where(Narrative.is_active == is_active)

    if min_confidence:
        confidence_levels = {"high": ["high"], "medium": ["high", "medium"], "low": ["high", "medium", "low"]}
        allowed = confidence_levels.get(min_confidence, ["high", "medium", "low"])
        query = query.where(Narrative.confidence.in_(allowed))

    # Count total before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Sort and paginate
    query = query.order_by(Narrative.velocity_score.desc(), Narrative.created_at.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query.options(selectinload(Narrative.ideas)))
    narratives = result.scalars().all()

    return NarrativeListResponse(
        narratives=[
            NarrativeResponse(
                id=n.id,
                title=n.title,
                summary=n.summary,
                confidence=n.confidence,
                confidence_reasoning=n.confidence_reasoning,
                is_active=n.is_active,
                velocity_score=n.velocity_score,
                rank=n.rank,
                tags=n.tags or [],
                key_evidence=n.key_evidence or [],
                supporting_source_names=n.supporting_source_names or [],
                idea_count=len(n.ideas) if n.ideas else 0,
                created_at=n.created_at,
                updated_at=n.updated_at,
                last_detected_at=n.last_detected_at,
            )
            for n in narratives
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{narrative_id}", response_model=NarrativeDetailResponse)
async def get_narrative(
    narrative_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single narrative with all its ideas and source details."""
    result = await db.execute(
        select(Narrative)
        .where(Narrative.id == narrative_id)
        .options(
            selectinload(Narrative.ideas),
            selectinload(Narrative.narrative_sources).selectinload(NarrativeSource.data_source),
        )
    )
    narrative = result.scalar_one_or_none()

    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")

    ideas = [
        IdeaInNarrative(
            id=idea.id,
            title=idea.title,
            description=idea.description,
            problem=idea.problem,
            solution=idea.solution,
            why_solana=idea.why_solana,
            scale_potential=idea.scale_potential,
            market_signals=idea.market_signals,
            supporting_signals=idea.supporting_signals or [],
            created_at=idea.created_at,
        )
        for idea in narrative.ideas
    ]

    sources = [
        NarrativeSourceResponse(
            data_source_name=ns.data_source.name if ns.data_source else "Unknown",
            data_source_url=ns.data_source.url if ns.data_source else "",
            signal_count=ns.signal_count,
        )
        for ns in narrative.narrative_sources
    ]

    # Supporting signal links (tweet/article URLs)
    sig_result = await db.execute(
        select(Signal, ScrapedContent, DataSource)
        .join(NarrativeSignalLink, NarrativeSignalLink.signal_id == Signal.id)
        .join(ScrapedContent, Signal.scraped_content_id == ScrapedContent.id)
        .join(DataSource, ScrapedContent.data_source_id == DataSource.id)
        .where(NarrativeSignalLink.narrative_id == narrative_id)
        .order_by(Signal.created_at.desc())
    )
    supporting_signals = [
        SupportingSignalResponse(
            signal_id=s.id,
            signal_title=s.signal_title,
            content_url=c.source_url,
            data_source_name=ds.name,
            data_source_url=ds.url,
        )
        for (s, c, ds) in sig_result.all()
    ]

    return NarrativeDetailResponse(
        id=narrative.id,
        title=narrative.title,
        summary=narrative.summary,
        confidence=narrative.confidence,
        confidence_reasoning=narrative.confidence_reasoning,
        is_active=narrative.is_active,
        velocity_score=narrative.velocity_score,
        rank=narrative.rank,
        tags=narrative.tags or [],
        key_evidence=narrative.key_evidence or [],
        supporting_source_names=narrative.supporting_source_names or [],
        ideas=ideas,
        sources=sources,
        supporting_signals=supporting_signals,
        created_at=narrative.created_at,
        updated_at=narrative.updated_at,
        last_detected_at=narrative.last_detected_at,
    )
