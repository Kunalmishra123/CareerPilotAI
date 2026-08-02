"""SQLAlchemy domain models and shared persistence concerns."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


def _utc_now() -> datetime:
    """Return the current UTC timestamp in SQLite-compatible naive form."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TimestampMixin:
    """Provide creation and update audit timestamps to persistent domain models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=_utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )


from domain.models.application import Application
from domain.models.company import Company
from domain.models.interview import Interview
from domain.models.job import Job
from domain.models.report import Report
from domain.models.resume import Resume

__all__ = [
    "Application",
    "Company",
    "Interview",
    "Job",
    "Report",
    "Resume",
    "TimestampMixin",
]
