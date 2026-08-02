"""Centralized Loguru configuration for CareerPilot AI."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, ClassVar, Mapping

from loguru import logger
from loguru._logger import Logger

from core.config import ConfigurationManager
from core.exceptions import ConfigurationError


DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_ROTATION = "00:00"
DEFAULT_LOG_RETENTION = "30 days"
DEFAULT_LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
    "{name}:{function}:{line} | {message}"
)
LOG_FILE_NAME = "career_pilot_{time:YYYY-MM-DD}.log"


@dataclass(frozen=True, slots=True)
class _LoggingConfiguration:
    """Immutable Loguru settings resolved from application configuration."""

    level: str = DEFAULT_LOG_LEVEL
    rotation: str = DEFAULT_LOG_ROTATION
    retention: str = DEFAULT_LOG_RETENTION
    format: str = DEFAULT_LOG_FORMAT


class LoggerManager:
    """Configure and provide the process-wide CareerPilot logger once.

    The manager owns the Loguru sinks it creates. Loguru synchronizes writes to
    each sink, allowing concurrent application threads to log safely.
    """

    _instance: ClassVar[LoggerManager | None] = None
    _instance_lock: ClassVar[Lock] = Lock()

    def __new__(
        cls,
        logs_directory: Path | None = None,
        logging_settings: Mapping[str, Any] | None = None,
    ) -> LoggerManager:
        """Return the process-wide logger manager, initializing it if necessary."""
        with cls._instance_lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialize(logs_directory, logging_settings)
                cls._instance = instance

        return cls._instance

    def __init__(
        self,
        logs_directory: Path | None = None,
        logging_settings: Mapping[str, Any] | None = None,
    ) -> None:
        """Provide an idempotent constructor for the singleton interface."""

    @property
    def log_directory(self) -> Path:
        """Return the directory containing the configured application log file."""
        return self._log_directory

    @property
    def log_file_path(self) -> Path:
        """Return the active log-file path pattern configured for Loguru."""
        return self._log_file_path

    def get_logger(self) -> Logger:
        """Return the configured Loguru logger instance."""
        return logger

    def _initialize(
        self,
        logs_directory: Path | None,
        logging_settings: Mapping[str, Any] | None,
    ) -> None:
        """Create logging sinks after resolving configuration and filesystem paths."""
        self._log_directory = self._resolve_logs_directory(logs_directory)
        self._log_directory.mkdir(parents=True, exist_ok=True)
        self._log_file_path = self._log_directory / LOG_FILE_NAME
        configuration = self._resolve_configuration(logging_settings)

        logger.remove()
        self._sink_ids = (
            logger.add(
                sys.stderr,
                level=configuration.level,
                format=configuration.format,
            ),
            logger.add(
                self._log_file_path,
                level=configuration.level,
                format=configuration.format,
                rotation=configuration.rotation,
                retention=configuration.retention,
                encoding="utf-8",
            ),
        )

    @classmethod
    def _resolve_logs_directory(cls, logs_directory: Path | None) -> Path:
        """Resolve a supplied log directory or the repository log directory."""
        if logs_directory is None:
            logs_directory = Path(__file__).resolve().parents[1] / "logs"

        return Path(logs_directory).expanduser().resolve()

    @classmethod
    def _resolve_configuration(
        cls,
        logging_settings: Mapping[str, Any] | None,
    ) -> _LoggingConfiguration:
        """Build validated logger settings from supplied or application settings."""
        settings = logging_settings if logging_settings is not None else cls._load_settings()
        return _LoggingConfiguration(
            level=cls._get_text_setting(settings, "level", DEFAULT_LOG_LEVEL),
            rotation=cls._get_text_setting(settings, "rotation", DEFAULT_LOG_ROTATION),
            retention=cls._get_text_setting(settings, "retention", DEFAULT_LOG_RETENTION),
            format=cls._get_text_setting(settings, "format", DEFAULT_LOG_FORMAT),
        )

    @staticmethod
    def _load_settings() -> Mapping[str, Any]:
        """Read the optional logging section without blocking logger startup."""
        try:
            settings = ConfigurationManager().get_settings()
        except ConfigurationError:
            return {}

        logging_settings = settings.get("logging", settings)
        return logging_settings if isinstance(logging_settings, Mapping) else {}

    @staticmethod
    def _get_text_setting(
        settings: Mapping[str, Any],
        name: str,
        default: str,
    ) -> str:
        """Return a non-empty text setting or its documented infrastructure default."""
        value = settings.get(name, default)
        return value.strip() if isinstance(value, str) and value.strip() else default


def get_logger() -> Logger:
    """Return the singleton, centrally configured Loguru logger."""
    return LoggerManager().get_logger()
