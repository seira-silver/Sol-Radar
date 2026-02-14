"""API endpoints for hackathon-relevant ideas."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.idea import Idea
from app.models.narrative import Narrative
from app.schemas.idea import IdeaResponse, IdeaListResponse

router = APIRouter(prefix="/hackathons", tags=["hackathons"])


@router.get("", response_model=IdeaListResponse)
async def list_hackathon_ideas(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    List ideas suitable for hackathons.

    Returns ideas from active narratives that are:
    - Tagged with "hackathon"
    - OR from high-velocity narratives (velocity_score > 5.0)
    """
    query = (
        select(Idea)
        .join(Narrative, Idea.narrative_id == Narrative.id)
        .where(
            Narrative.is_active == True,  # noqa: E712
            or_(
                Narrative.tags.contains(["hackathon"]),
                Narrative.velocity_score > 5.0,
            ),
        )
    )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Sort by narrative velocity (highest opportunity first)
    query = (
        query.order_by(Narrative.velocity_score.desc(), Idea.created_at.desc())
        .offset(offset)
        .limit(limit)
        .options(selectinload(Idea.narrative))
    )

    result = await db.execute(query)
    ideas = result.scalars().all()

    return IdeaListResponse(
        ideas=[
            IdeaResponse(
                id=idea.id,
                narrative_id=idea.narrative_id,
                narrative_title=idea.narrative.title if idea.narrative else "",
                narrative_is_active=idea.narrative.is_active if idea.narrative else True,
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
            for idea in ideas
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
