"""Narrative and NarrativeSource models — detected narratives from Stage 2 synthesis."""

from datetime import datetime
from sqlalchemy import String, Text, Float, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.helpers import utcnow


class Narrative(Base):
    __tablename__ = "narratives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "high" | "medium" | "low"
    confidence_reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    velocity_score: Mapped[float] = mapped_column(Float, default=0.0)
    rank: Mapped[int] = mapped_column(Integer, nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    key_evidence: Mapped[list] = mapped_column(JSONB, default=list)
    supporting_source_names: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    last_detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    # Relationships
    ideas: Mapped[list["Idea"]] = relationship(
        "Idea", back_populates="narrative", lazy="selectin", cascade="all, delete-orphan"
    )
    narrative_sources: Mapped[list["NarrativeSource"]] = relationship(
        "NarrativeSource", back_populates="narrative", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Narrative(id={self.id}, title='{self.title[:40]}...', active={self.is_active})>"


class NarrativeSource(Base):
    __tablename__ = "narrative_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    narrative_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("narratives.id", ondelete="CASCADE"), nullable=False
    )
    data_source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False
    )
    signal_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    narrative: Mapped["Narrative"] = relationship(
        "Narrative", back_populates="narrative_sources"
    )
    data_source: Mapped["DataSource"] = relationship("DataSource")

    def __repr__(self) -> str:
        return f"<NarrativeSource(narrative_id={self.narrative_id}, source_id={self.data_source_id})>"
