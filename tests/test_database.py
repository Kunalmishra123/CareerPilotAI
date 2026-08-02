"""Unit tests for CareerPilot SQLAlchemy database infrastructure."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from sqlalchemy import Column, Integer, MetaData, Table, func, insert, select
from sqlalchemy.orm import Session

from database.connection import DatabaseConnection, get_engine
from database.session import SessionManager


class DatabaseInfrastructureTests(unittest.TestCase):
    """Verify SQLite engine and transactional session infrastructure."""

    def setUp(self) -> None:
        """Create an isolated database path and its corresponding engine."""
        self._temporary_directory = TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "storage" / "test.db"
        self.connection = DatabaseConnection(self.database_path)
        self.session_manager = SessionManager(self.connection.engine)
        self.metadata = MetaData()
        self.transaction_table = Table(
            "transaction_test",
            self.metadata,
            Column("id", Integer, primary_key=True),
        )
        self.metadata.create_all(self.connection.engine)

    def tearDown(self) -> None:
        """Dispose the engine before removing its temporary database directory."""
        self.connection.dispose()
        self._temporary_directory.cleanup()

    def test_creates_storage_directory_and_database_file(self) -> None:
        """Create the parent storage directory and SQLite file during initialization."""
        self.assertTrue(self.database_path.parent.is_dir())
        self.assertTrue(self.database_path.is_file())

    def test_initializes_a_sqlite_engine(self) -> None:
        """Expose a usable SQLAlchemy engine configured for SQLite."""
        engine = get_engine(self.database_path)

        self.assertIs(engine, self.connection.engine)
        self.assertEqual("sqlite", engine.dialect.name)

    def test_creates_and_closes_a_session(self) -> None:
        """Yield a session and close it after the context manager exits."""
        session = Session(self.connection.engine)
        with patch.object(self.session_manager, "_session_factory", return_value=session):
            with patch.object(session, "close", wraps=session.close) as close:
                with self.session_manager.session_scope() as active_session:
                    self.assertIs(session, active_session)

                close.assert_called_once()

    def test_commits_successful_transactions(self) -> None:
        """Persist changes when a session scope completes without an exception."""
        with self.session_manager.session_scope() as session:
            session.execute(insert(self.transaction_table).values(id=1))

        self.assertEqual(1, self._count_rows())

    def test_rolls_back_transactions_when_an_exception_occurs(self) -> None:
        """Discard uncommitted changes when work inside a session scope fails."""
        with self.assertRaises(RuntimeError):
            with self.session_manager.session_scope() as session:
                session.execute(insert(self.transaction_table).values(id=1))
                raise RuntimeError("Transaction failure")

        self.assertEqual(0, self._count_rows())

    def test_supports_multiple_independent_sessions(self) -> None:
        """Allow separate sessions to commit and read data through the same engine."""
        with self.session_manager.session_scope() as first_session:
            first_session.execute(insert(self.transaction_table).values(id=1))

        with self.session_manager.session_scope() as second_session:
            self.assertEqual(1, second_session.scalar(select(func.count()).select_from(self.transaction_table)))

    def _count_rows(self) -> int:
        """Return the number of rows created by the transaction test table."""
        with self.session_manager.session_scope() as session:
            return session.scalar(select(func.count()).select_from(self.transaction_table)) or 0


if __name__ == "__main__":
    unittest.main()
