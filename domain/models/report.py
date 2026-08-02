"""Report persistence model."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Integer, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from domain.models import TimestampMixin


class Report(TimestampMixin, Base):
    """Represent an exported application report generated for a reporting period."""

    __tablename__ = "reports"
    __table_args__ = (UniqueConstraint("report_date", name="uq_reports_report_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    india_jobs_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    international_jobs_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    india_jobs_applied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    international_jobs_applied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_jobs_applied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejections: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    offers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    platform_summary: Mapped[dict[str, int] | None] = mapped_column(JSON, nullable=True)
