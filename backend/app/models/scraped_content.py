"""ScrapedContent model — stores raw scraped data with source links.

Analysis status state machine:
  pending → processing → completed   (happy path)
  pending → processing → failed      (LLM error, retryable up to MAX_ANALYSIS_ATTEMPTS)
  pending → skipped                   (content too short, not relevant, etc.)

The (content_hash, data_source_id) unique constraint prevents duplicate storage
at the DB level, so even concurrent scrapers can't double-insert.
"""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.helpers import utcnow

# Maximum times we'll retry LLM analysis on a failed content item
MAX_ANALYSIS_ATTEMPTS = 3


class ScrapedContent(Base):
    __tablename__ = "scraped_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data_source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False
    )
    source_url: Mapped[str] = mapped_column(
        String(2048), nullable=False
    )  # Direct link to article/tweet/post
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # SHA-256 for dedup

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    # ── Analysis tracking ──
    # Status: pending | processing | completed | failed | skipped
    analysis_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    analysis_attempts: Mapped[int] = mapped_column(Integer, default=0)
    analyzed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    analysis_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Keep is_analyzed as a computed convenience (for backward compat)
    @property
    def is_analyzed(self) -> bool:
        return self.analysis_status in ("completed", "skipped")

    # Relationships
    data_source: Mapped["DataSource"] = relationship(
        "DataSource", back_populates="scraped_contents"
    )
    signals: Mapped[list["Signal"]] = relationship(
        "Signal", back_populates="scraped_content", lazy="selectin"
    )

    __table_args__ = (
        # Prevent duplicate content from the same source at DB level
        UniqueConstraint("content_hash", "data_source_id", name="uq_content_hash_source"),
        Index("ix_scraped_content_hash_source", "content_hash", "data_source_id"),
        Index("ix_scraped_content_analysis_status", "analysis_status"),
    )

    def __repr__(self) -> str:
        return (
            f"<ScrapedContent(id={self.id}, status={self.analysis_status}, "
            f"url='{self.source_url[:50]}...')>"
        )
