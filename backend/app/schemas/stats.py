"""Pydantic schemas for Stats API responses."""

from datetime import datetime
from pydantic import BaseModel


class StatsResponse(BaseModel):
    active_narratives_count: int
    total_narratives_count: int
    total_ideas_count: int
    avg_velocity_score: float
    active_builders: int  # unique project count from signals
    sources_scraped_count: int
    total_signals_count: int
    last_web_scrape_time: datetime | None
    last_twitter_scrape_time: datetime | None
    next_synthesis_time: datetime | None
