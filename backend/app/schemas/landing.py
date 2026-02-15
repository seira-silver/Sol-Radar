"""Pydantic schemas for landing/dashboard API responses."""

from pydantic import BaseModel

from app.schemas.narrative import NarrativeResponse, IdeaInNarrative
from app.schemas.stats import StatsResponse


class LandingNarrativeResponse(NarrativeResponse):
    ideas: list[IdeaInNarrative] = []


class LandingNarrativesResponse(BaseModel):
    narratives: list[LandingNarrativeResponse]
    total: int
    limit: int
    offset: int


class LandingResponse(BaseModel):
    stats: StatsResponse
    narratives: LandingNarrativesResponse

