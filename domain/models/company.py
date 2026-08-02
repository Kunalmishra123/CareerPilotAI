"""Company persistence model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from domain.models import TimestampMixin

if TYPE_CHECKING:
    from domain.models.job import Job


class Company(TimestampMixin, Base):
    """Represent an employer associated with one or more discovered jobs."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    career_page: Mapped[str | None] = mapped_column(String(500), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True)

    jobs: Mapped[list[Job]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
