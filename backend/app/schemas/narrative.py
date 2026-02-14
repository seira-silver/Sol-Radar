"""Pydantic schemas for Narrative API responses."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NarrativeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str
    confidence: str
    confidence_reasoning: str
    is_active: bool
    velocity_score: float
    rank: int | None
    tags: list[str]
    key_evidence: list[str]
    supporting_source_names: list[str]
    idea_count: int = 0
    created_at: datetime
    updated_at: datetime
    last_detected_at: datetime


class NarrativeListResponse(BaseModel):
    narratives: list[NarrativeResponse]
    total: int
    limit: int
    offset: int


class IdeaInNarrative(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    problem: str
    solution: str
    why_solana: str
    scale_potential: str
    market_signals: str | None
    supporting_signals: list[str]
    created_at: datetime


class NarrativeSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data_source_name: str
    data_source_url: str
    signal_count: int


class NarrativeDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str
    confidence: str
    confidence_reasoning: str
    is_active: bool
    velocity_score: float
    rank: int | None
    tags: list[str]
    key_evidence: list[str]
    supporting_source_names: list[str]
    ideas: list[IdeaInNarrative]
    sources: list[NarrativeSourceResponse]
    created_at: datetime
    updated_at: datetime
    last_detected_at: datetime
