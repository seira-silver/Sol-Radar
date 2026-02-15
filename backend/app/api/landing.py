"""API endpoints for landing page (bundle common queries)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.stats import get_stats
from app.database import get_db
from app.models.narrative import Narrative
from app.schemas.landing import (
    LandingNarrativeResponse,
    LandingNarrativesResponse,
    LandingResponse,
)
from app.schemas.narrative import IdeaInNarrative

router = APIRouter(prefix="/landing", tags=["landing"])


@router.get("", response_model=LandingResponse)
async def get_landing(
    # Narratives
    narratives_is_active: bool | None = Query(True, description="Filter narratives by active status"),
    narratives_min_confidence: str | None = Query(
        None, description="Minimum confidence: high, medium, low"
    ),
    narratives_tags: str | None = Query(None, description="Comma-separated narrative tags to filter by"),
    narratives_limit: int = Query(10, ge=1, le=50),
    narratives_offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Return landing payload: stats + narratives with nested ideas."""

    # --- Narratives (same mapping as /narratives) ---
    n_query = select(Narrative)

    if narratives_is_active is not None:
        n_query = n_query.where(Narrative.is_active == narratives_is_active)

    if narratives_min_confidence:
        confidence_levels = {
            "high": ["high"],
            "medium": ["high", "medium"],
            "low": ["high", "medium", "low"],
        }
        allowed = confidence_levels.get(narratives_min_confidence, ["high", "medium", "low"])
        n_query = n_query.where(Narrative.confidence.in_(allowed))

    if narratives_tags:
        tag_list = [t.strip() for t in narratives_tags.split(",") if t.strip()]
        for tag in tag_list:
            n_query = n_query.where(Narrative.tags.contains([tag]))

    n_count_query = select(func.count()).select_from(n_query.subquery())
    n_total_result = await db.execute(n_count_query)
    n_total = n_total_result.scalar() or 0

    n_query = (
        n_query.order_by(Narrative.velocity_score.desc(), Narrative.created_at.desc())
        .offset(narratives_offset)
        .limit(narratives_limit)
    )
    n_result = await db.execute(n_query.options(selectinload(Narrative.ideas)))
    narratives = n_result.scalars().all()

    narratives_resp = LandingNarrativesResponse(
        narratives=[
            LandingNarrativeResponse(
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
                ideas=[
                    IdeaInNarrative.model_validate(idea)
                    for idea in sorted((n.ideas or []), key=lambda i: i.created_at, reverse=True)
                ],
                created_at=n.created_at,
                updated_at=n.updated_at,
                last_detected_at=n.last_detected_at,
            )
            for n in narratives
        ],
        total=n_total,
        limit=narratives_limit,
        offset=narratives_offset,
    )

    stats = await get_stats(db=db)
    return LandingResponse(stats=stats, narratives=narratives_resp)

