"""Job persistence model."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from domain.models import TimestampMixin

if TYPE_CHECKING:
    from domain.models.application import Application
    from domain.models.company import Company


class Job(TimestampMixin, Base):
    """Represent a normalized job discovered through a supported platform."""

    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_company_platform", "company_id", "platform"),
        Index("ix_jobs_title", "title"),
        Index("ix_jobs_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(100), nullable=False)
    job_url: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    work_mode: Mapped[str | None] = mapped_column(String(100), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(100), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    visa_sponsorship: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    match_score: Mapped[float | None] = mapped_column(Float, index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    posted_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    company: Mapped[Company] = relationship(back_populates="jobs")
    applications: Mapped[list[Application]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
