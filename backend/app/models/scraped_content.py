"""ScrapedContent model — stores raw scraped data with source links."""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.helpers import utcnow


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
    is_analyzed: Mapped[bool] = mapped_column(default=False)

    # Relationships
    data_source: Mapped["DataSource"] = relationship(
        "DataSource", back_populates="scraped_contents"
    )
    signals: Mapped[list["Signal"]] = relationship(
        "Signal", back_populates="scraped_content", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_scraped_content_hash_source", "content_hash", "data_source_id"),
    )

    def __repr__(self) -> str:
        return f"<ScrapedContent(id={self.id}, url='{self.source_url[:60]}...')>"
