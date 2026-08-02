"""Interview persistence model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from domain.models import TimestampMixin

if TYPE_CHECKING:
    from domain.models.application import Application


class Interview(TimestampMixin, Base):
    """Represent an interview invitation or completed interview for an application."""

    __tablename__ = "interviews"
    __table_args__ = (Index("ix_interviews_scheduled_at", "scheduled_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    round: Mapped[str] = mapped_column(String(100), nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    interviewer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meeting_link: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    questions: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(String(255), nullable=True)

    application: Mapped[Application] = relationship(back_populates="interviews")
