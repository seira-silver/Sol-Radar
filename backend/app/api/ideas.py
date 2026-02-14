"""API endpoints for ideas."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.idea import Idea
from app.models.narrative import Narrative
from app.schemas.idea import IdeaResponse, IdeaListResponse

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.get("", response_model=IdeaListResponse)
async def list_ideas(
    narrative_id: int | None = Query(None, description="Filter by narrative ID"),
    tags: str | None = Query(None, description="Comma-separated tags to match against narrative tags"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List ideas with optional narrative and tag filtering."""
    query = select(Idea).join(Narrative, Idea.narrative_id == Narrative.id)

    if narrative_id is not None:
        query = query.where(Idea.narrative_id == narrative_id)

    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        for tag in tag_list:
            query = query.where(Narrative.tags.contains([tag]))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Sort and paginate
    query = query.order_by(Idea.created_at.desc())
    query = query.offset(offset).limit(limit)
    query = query.options(selectinload(Idea.narrative))

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
