"""Pydantic schemas for Signal API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SignalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scraped_content_id: int
    signal_title: str
    description: str
    signal_type: str
    novelty: str
    evidence: str
    related_projects: list[object]
    tags: list[object]
    created_at: datetime

    # Enriched fields (joined from scraped_content + data_sources)
    content_url: str
    content_title: str | None = None
    scraped_at: datetime
    data_source_id: int
    data_source_name: str
    data_source_url: str
    data_source_type: str
    data_source_category: str


class SignalListResponse(BaseModel):
    signals: list[SignalResponse]
    total: int
    limit: int
    offset: int


class SignalDetailResponse(SignalResponse):
    """Currently identical to SignalResponse; kept for forward compatibility."""

