"""Resume persistence model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from domain.models import TimestampMixin

if TYPE_CHECKING:
    from domain.models.application import Application


class Resume(TimestampMixin, Base):
    """Represent a verified master resume or a generated tailored version."""

    __tablename__ = "resumes"
    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    summary: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    applications: Mapped[list[Application]] = relationship(back_populates="resume")
