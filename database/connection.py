"""SQLite engine creation and lifecycle management for CareerPilot AI."""

from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import ClassVar

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

from core.logger import get_logger


DATABASE_FILE_NAME = "careerpilot.db"


class DatabaseConnection:
    """Create one thread-safe SQLAlchemy engine for each SQLite database path."""

    _instances: ClassVar[dict[Path, DatabaseConnection]] = {}
    _instances_lock: ClassVar[Lock] = Lock()

    def __new__(cls, database_path: Path | None = None) -> DatabaseConnection:
        """Return the cached connection manager for the resolved database path."""
        resolved_path = cls._resolve_database_path(database_path)

        with cls._instances_lock:
            instance = cls._instances.get(resolved_path)
            if instance is None:
                instance = super().__new__(cls)
                instance._initialize(resolved_path)
                cls._instances[resolved_path] = instance

        return instance

    def __init__(self, database_path: Path | None = None) -> None:
        """Provide an idempotent constructor for cached connection managers."""

    @property
    def database_path(self) -> Path:
        """Return the resolved SQLite database file path."""
        return self._database_path

    @property
    def engine(self) -> Engine:
        """Return the initialized SQLAlchemy engine."""
        return self._engine

    def dispose(self) -> None:
        """Release pooled connections and remove this instance from the cache."""
        self._engine.dispose()
        with self._instances_lock:
            if self._instances.get(self._database_path) is self:
                del self._instances[self._database_path]

    def _initialize(self, database_path: Path) -> None:
        """Create the storage directory, engine, and SQLite database file."""
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._database_path = database_path
        self._engine = create_engine(
            self._build_database_url(database_path),
            future=True,
            poolclass=QueuePool,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )

        with self._engine.connect():
            pass

        get_logger().info("SQLite database initialized at {}", database_path)

    @classmethod
    def _resolve_database_path(cls, database_path: Path | None) -> Path:
        """Resolve a supplied path or the standard application storage location."""
        if database_path is None:
            database_path = Path(__file__).resolve().parents[1] / "storage" / DATABASE_FILE_NAME

        return Path(database_path).expanduser().resolve()

    @staticmethod
    def _build_database_url(database_path: Path) -> str:
        """Build a cross-platform SQLAlchemy URL for an absolute SQLite path."""
        return f"sqlite:///{database_path.as_posix()}"


def get_engine(database_path: Path | None = None) -> Engine:
    """Return the cached SQLAlchemy engine for the selected SQLite database."""
    return DatabaseConnection(database_path).engine
