"""Transactional SQLAlchemy session management for CareerPilot AI."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from core.logger import get_logger
from database.connection import get_engine


class SessionManager:
    """Create short-lived SQLAlchemy sessions with safe transaction handling."""

    def __init__(self, engine: Engine | None = None) -> None:
        """Create a session factory bound to the supplied or default database engine."""
        self._session_factory = sessionmaker(
            bind=engine or get_engine(),
            autoflush=False,
            expire_on_commit=False,
        )

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Yield a session, committing on success and rolling back on failure."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            get_logger().exception("Database transaction rolled back")
            raise
        finally:
            session.close()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Yield a transactional session bound to the default SQLite engine."""
    with SessionManager().session_scope() as session:
        yield session
