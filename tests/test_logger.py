"""Unit tests for the centralized Loguru logging system."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from loguru import logger as loguru_logger

from core.logger import LoggerManager, get_logger


class LoggerManagerTests(unittest.TestCase):
    """Verify centralized logger initialization and file output behavior."""

    def setUp(self) -> None:
        """Create an isolated directory and reset the singleton for each test."""
        LoggerManager._instance = None
        loguru_logger.remove()
        self._temporary_directory = TemporaryDirectory()
        self.logs_directory = Path(self._temporary_directory.name) / "logs"

    def tearDown(self) -> None:
        """Flush asynchronous sinks and release temporary test resources."""
        loguru_logger.complete()
        loguru_logger.remove()
        LoggerManager._instance = None
        self._temporary_directory.cleanup()

    def test_initializes_the_logger_and_creates_the_log_directory(self) -> None:
        """Create the target log directory during logger initialization."""
        manager = LoggerManager(self.logs_directory)

        self.assertTrue(manager.log_directory.is_dir())
        self.assertIs(loguru_logger, manager.get_logger())

    def test_uses_a_single_manager_and_logger_instance(self) -> None:
        """Reuse the configured logger for repeated initialization requests."""
        first_manager = LoggerManager(self.logs_directory)
        second_manager = LoggerManager(self.logs_directory)

        self.assertIs(first_manager, second_manager)
        self.assertIs(first_manager.get_logger(), second_manager.get_logger())

    def test_get_logger_returns_the_same_logger_on_multiple_calls(self) -> None:
        """Expose one stable logger through the public module-level function."""
        LoggerManager(self.logs_directory)

        self.assertIs(get_logger(), get_logger())

    def test_writes_a_log_message_to_a_utf8_file(self) -> None:
        """Persist a log message to the configured rotating log-file sink."""
        manager = LoggerManager(
            self.logs_directory,
            {"level": "INFO", "rotation": "1 day", "retention": "1 day"},
        )
        message = "Logger file output verification"

        manager.get_logger().info(message)
        manager.get_logger().complete()

        log_files = list(manager.log_directory.glob("career_pilot_*.log"))
        self.assertEqual(1, len(log_files))
        self.assertIn(message, log_files[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
