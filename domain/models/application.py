"""Application persistence model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from domain.models import TimestampMixin

if TYPE_CHECKING:
    from domain.models.interview import Interview
    from domain.models.job import Job
    from domain.models.resume import Resume


class Application(TimestampMixin, Base):
    """Represent one auditable application submitted for a job."""

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    resume_id: Mapped[int | None] = mapped_column(ForeignKey("resumes.id"), nullable=True)
    cover_letter_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    platform: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    job: Mapped[Job] = relationship(back_populates="applications")
    resume: Mapped[Resume | None] = relationship(back_populates="applications")
    interviews: Mapped[list[Interview]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
    )
