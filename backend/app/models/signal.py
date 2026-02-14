"""Signal model — individual signals extracted by Stage 1 LLM analysis."""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.helpers import utcnow


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scraped_content_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scraped_content.id", ondelete="CASCADE"), nullable=False
    )
    signal_title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    signal_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "onchain" | "developer" | "social" | "research" | "mobile" | "other"
    novelty: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )  # "high" | "medium" | "low"
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    related_projects: Mapped[list] = mapped_column(JSONB, default=list)
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    # Relationships
    scraped_content: Mapped["ScrapedContent"] = relationship(
        "ScrapedContent", back_populates="signals"
    )

    def __repr__(self) -> str:
        return f"<Signal(id={self.id}, title='{self.signal_title[:40]}...')>"
