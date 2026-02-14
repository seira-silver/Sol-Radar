"""Pydantic schemas for Idea API responses."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class IdeaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    narrative_id: int
    narrative_title: str = ""
    narrative_is_active: bool = True
    title: str
    description: str
    problem: str
    solution: str
    why_solana: str
    scale_potential: str
    market_signals: str | None
    supporting_signals: list[str]
    created_at: datetime


class IdeaListResponse(BaseModel):
    ideas: list[IdeaResponse]
    total: int
    limit: int
    offset: int
