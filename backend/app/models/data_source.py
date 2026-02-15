"""DataSource model — tracks each scraping target (web URL or Twitter KOL)."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.helpers import utcnow


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "web" | "twitter" | "reddit" | "pdf"
    source_category: Mapped[str] = mapped_column(
        String(100), nullable=False, default="general"
    )  # "ecosystem_news" | "research" | "community" | "social_kol"
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )  # "high" | "medium" | "low"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    # Relationships
    scraped_contents: Mapped[list["ScrapedContent"]] = relationship(
        "ScrapedContent", back_populates="data_source", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<DataSource(id={self.id}, name='{self.name}', type='{self.source_type}')>"
