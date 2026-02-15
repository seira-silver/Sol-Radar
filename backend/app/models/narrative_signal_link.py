"""Link table between Narratives and Signals.

This provides end-to-end traceability:
Narrative -> supporting Signal(s) -> ScrapedContent.source_url (tweet/article link)
and DataSource.url (profile/feed/root).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.helpers import utcnow


class NarrativeSignalLink(Base):
    __tablename__ = "narrative_signal_links"
    __table_args__ = (
        UniqueConstraint("narrative_id", "signal_id", name="uq_narrative_signal"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    narrative_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("narratives.id", ondelete="CASCADE"), nullable=False, index=True
    )
    signal_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    narrative: Mapped["Narrative"] = relationship("Narrative")
    signal: Mapped["Signal"] = relationship("Signal")

