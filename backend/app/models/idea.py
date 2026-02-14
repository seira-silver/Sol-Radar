"""Idea model — product ideas generated per narrative (3-5 each)."""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.helpers import utcnow


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    narrative_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("narratives.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    solution: Mapped[str] = mapped_column(Text, nullable=False)
    why_solana: Mapped[str] = mapped_column(Text, nullable=False)
    scale_potential: Mapped[str] = mapped_column(Text, nullable=False)
    market_signals: Mapped[str] = mapped_column(Text, nullable=True)
    supporting_signals: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    # Relationships
    narrative: Mapped["Narrative"] = relationship("Narrative", back_populates="ideas")

    def __repr__(self) -> str:
        return f"<Idea(id={self.id}, title='{self.title[:40]}...')>"
