"""API endpoints for dashboard statistics."""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.narrative import Narrative
from app.models.idea import Idea
from app.models.signal import Signal
from app.models.data_source import DataSource
from app.models.scraped_content import ScrapedContent
from app.schemas.stats import StatsResponse
from app.config import get_settings

router = APIRouter(prefix="/stats", tags=["stats"])

settings = get_settings()


@router.get("", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics: active narratives, ideas, velocity, builders, etc."""

    # Active narratives count
    active_result = await db.execute(
        select(func.count(Narrative.id)).where(Narrative.is_active == True)  # noqa: E712
    )
    active_narratives = active_result.scalar() or 0

    # Total narratives count
    total_narratives_result = await db.execute(select(func.count(Narrative.id)))
    total_narratives = total_narratives_result.scalar() or 0

    # Total ideas
    ideas_result = await db.execute(select(func.count(Idea.id)))
    total_ideas = ideas_result.scalar() or 0

    # Average velocity score (active narratives only)
    avg_vel_result = await db.execute(
        select(func.avg(Narrative.velocity_score)).where(Narrative.is_active == True)  # noqa: E712
    )
    avg_velocity = round(avg_vel_result.scalar() or 0.0, 3)

    # Active builders — count unique project names across all signals
    # We extract from the related_projects JSON array
    signals_result = await db.execute(select(Signal.related_projects))
    all_projects: set[str] = set()
    for (projects,) in signals_result:
        if projects:
            for p in projects:
                if isinstance(p, str) and p.strip():
                    all_projects.add(p.strip().lower())
    active_builders = len(all_projects)

    # Total signals
    signals_count_result = await db.execute(select(func.count(Signal.id)))
    total_signals = signals_count_result.scalar() or 0

    # Sources scraped — count active data sources
    sources_result = await db.execute(
        select(func.count(DataSource.id)).where(DataSource.is_active == True)  # noqa: E712
    )
    sources_count = sources_result.scalar() or 0

    # Last scrape times
    last_web_result = await db.execute(
        select(func.max(DataSource.last_scraped_at)).where(DataSource.source_type == "web")
    )
    last_web_scrape = last_web_result.scalar()

    last_twitter_result = await db.execute(
        select(func.max(DataSource.last_scraped_at)).where(DataSource.source_type == "twitter")
    )
    last_twitter_scrape = last_twitter_result.scalar()

    # Next synthesis time — approximate
    from datetime import timedelta
    from app.utils.helpers import utcnow

    last_narrative_result = await db.execute(
        select(func.max(Narrative.created_at))
    )
    last_synthesis = last_narrative_result.scalar()
    if last_synthesis:
        next_synthesis = last_synthesis + timedelta(days=settings.NARRATIVE_SYNTHESIS_INTERVAL_DAYS)
    else:
        next_synthesis = utcnow()  # Will run soon if never run

    return StatsResponse(
        active_narratives_count=active_narratives,
        total_narratives_count=total_narratives,
        total_ideas_count=total_ideas,
        avg_velocity_score=avg_velocity,
        active_builders=active_builders,
        sources_scraped_count=sources_count,
        total_signals_count=total_signals,
        last_web_scrape_time=last_web_scrape,
        last_twitter_scrape_time=last_twitter_scrape,
        next_synthesis_time=next_synthesis,
    )
