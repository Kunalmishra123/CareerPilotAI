"""Immutable YAML configuration loading for CareerPilot AI.

This module is intentionally limited to application infrastructure.  It loads
and validates the required configuration files without interpreting any of
their business-specific values.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from types import MappingProxyType
from typing import Any, ClassVar, Mapping

import yaml
from loguru import logger

from core.exceptions import (
    ConfigurationError,
    ConfigurationFileMissingError,
    ConfigurationParseError,
    EmptyConfigurationError,
)


@dataclass(frozen=True, slots=True)
class ConfigurationSnapshot:
    """Immutable collection of the configuration documents required at startup."""

    settings: Mapping[str, Any]
    user_profile: Mapping[str, Any]
    platforms: Mapping[str, Any]
    prompts: Mapping[str, Any]


class ConfigurationManager:
    """Load and provide immutable application configuration from YAML files.

    The manager is a process-wide singleton.  The first construction loads the
    configuration; subsequent constructions return that loaded instance.  A
    different configuration directory cannot be introduced afterwards, which
    prevents accidental runtime configuration changes.
    """

    REQUIRED_CONFIG_FILES: ClassVar[Mapping[str, str]] = MappingProxyType(
        {
            "settings": "settings.yaml",
            "user_profile": "user_profile.yaml",
            "platforms": "platforms.yaml",
            "prompts": "prompts.yaml",
        }
    )
    _instance: ClassVar[ConfigurationManager | None] = None
    _instance_lock: ClassVar[Lock] = Lock()

    def __new__(
        cls,
        config_directory: Path | None = None,
    ) -> ConfigurationManager:
        """Return the one configuration manager instance for this process."""
        requested_directory = cls._resolve_config_directory(config_directory)

        with cls._instance_lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialize(requested_directory)
                cls._instance = instance
            elif cls._instance.config_directory != requested_directory:
                raise ConfigurationError(
                    "ConfigurationManager is already initialized with a "
                    f"different directory: {cls._instance.config_directory}"
                )

        return cls._instance

    def __init__(self, config_directory: Path | None = None) -> None:
        """Initialize the singleton interface without reloading configuration."""

    @property
    def config_directory(self) -> Path:
        """Return the resolved directory from which configuration was loaded."""
        return self._config_directory

    def get_settings(self) -> Mapping[str, Any]:
        """Return the immutable contents of ``settings.yaml``."""
        return self._configuration.settings

    def get_user_profile(self) -> Mapping[str, Any]:
        """Return the immutable contents of ``user_profile.yaml``."""
        return self._configuration.user_profile

    def get_platforms(self) -> Mapping[str, Any]:
        """Return the immutable contents of ``platforms.yaml``."""
        return self._configuration.platforms

    def get_prompts(self) -> Mapping[str, Any]:
        """Return the immutable contents of ``prompts.yaml``."""
        return self._configuration.prompts

    def _initialize(self, config_directory: Path) -> None:
        """Load all required documents once during singleton creation."""
        self._config_directory = config_directory
        loaded_documents = {
            name: self._load_document(config_directory / file_name)
            for name, file_name in self.REQUIRED_CONFIG_FILES.items()
        }
        self._configuration = ConfigurationSnapshot(**loaded_documents)
        logger.info("Configuration loaded from {}", config_directory)

    @classmethod
    def _resolve_config_directory(cls, config_directory: Path | None) -> Path:
        """Resolve the supplied directory or the repository configuration directory."""
        if config_directory is None:
            config_directory = Path(__file__).resolve().parents[1] / "config"

        return Path(config_directory).expanduser().resolve()

    @staticmethod
    def _load_document(file_path: Path) -> Mapping[str, Any]:
        """Parse, validate, and freeze one required YAML configuration document."""
        if not file_path.is_file():
            logger.error("Required configuration file is missing: {}", file_path)
            raise ConfigurationFileMissingError(
                f"Required configuration file is missing: {file_path}"
            )

        try:
            with file_path.open(encoding="utf-8") as config_file:
                document = yaml.safe_load(config_file)
        except yaml.YAMLError as error:
            logger.exception("Invalid YAML configuration file: {}", file_path)
            raise ConfigurationParseError(
                f"Invalid YAML in configuration file: {file_path}"
            ) from error
        except OSError as error:
            logger.exception("Unable to read configuration file: {}", file_path)
            raise ConfigurationError(
                f"Unable to read configuration file: {file_path}"
            ) from error

        if not document:
            logger.error("Configuration file is empty: {}", file_path)
            raise EmptyConfigurationError(
                f"Configuration file is empty: {file_path}"
            )
        if not isinstance(document, dict):
            logger.error("Configuration file must contain a YAML mapping: {}", file_path)
            raise ConfigurationParseError(
                f"Configuration file must contain a YAML mapping: {file_path}"
            )

        return _freeze(document)


def _freeze(value: Any) -> Any:
    """Recursively convert mutable YAML values into immutable equivalents."""
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value
