"""SQLAlchemy declarative base shared by future CareerPilot ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class from which all future CareerPilot ORM models will inherit."""
