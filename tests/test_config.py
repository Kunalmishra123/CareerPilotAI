"""Unit tests for the immutable YAML configuration system."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from types import MappingProxyType
import unittest

from core.config import (
    ConfigurationError,
    ConfigurationFileMissingError,
    ConfigurationManager,
    ConfigurationParseError,
    EmptyConfigurationError,
)
from core.exceptions import ConfigurationError as SharedConfigurationError


class ConfigurationManagerTests(unittest.TestCase):
    """Verify loading, validation, singleton behavior, and immutability."""

    def setUp(self) -> None:
        """Start each test with no previously initialized singleton."""
        ConfigurationManager._instance = None
        self._temporary_directory = TemporaryDirectory()
        self.config_directory = Path(self._temporary_directory.name)

    def tearDown(self) -> None:
        """Clean up the temporary configuration directory and singleton state."""
        ConfigurationManager._instance = None
        self._temporary_directory.cleanup()

    def test_loads_all_required_documents_as_immutable_mappings(self) -> None:
        """Load every required YAML document and recursively freeze its values."""
        self._write_valid_configuration()

        manager = ConfigurationManager(self.config_directory)

        settings = manager.get_settings()
        self.assertEqual("INFO", settings["logging"]["level"])
        self.assertEqual(("C#", ".NET"), manager.get_user_profile()["skills"])
        self.assertIsInstance(settings, MappingProxyType)
        self.assertIsInstance(settings["logging"], MappingProxyType)
        self.assertIsInstance(manager.get_platforms(), MappingProxyType)
        self.assertIsInstance(manager.get_prompts(), MappingProxyType)
        with self.assertRaises(TypeError):
            settings["mode"] = "automatic"  # type: ignore[index]
        with self.assertRaises(TypeError):
            manager.get_platforms()["naukri"] = {}  # type: ignore[index]
        with self.assertRaises(TypeError):
            manager.get_prompts()["cover_letter"] = {}  # type: ignore[index]

    def test_returns_the_same_singleton_for_the_same_directory(self) -> None:
        """Reuse the loaded configuration instance instead of rereading files."""
        self._write_valid_configuration()

        first_manager = ConfigurationManager(self.config_directory)
        second_manager = ConfigurationManager(self.config_directory)

        self.assertIs(first_manager, second_manager)

    def test_rejects_a_different_directory_after_initialization(self) -> None:
        """Prevent configuration from changing after the singleton is loaded."""
        self._write_valid_configuration()
        manager = ConfigurationManager(self.config_directory)
        alternate_directory = self.config_directory / "alternate"
        alternate_directory.mkdir()

        with self.assertRaises(ConfigurationError):
            ConfigurationManager(alternate_directory)

        self.assertEqual(self.config_directory.resolve(), manager.config_directory)

    def test_raises_when_a_required_file_is_missing(self) -> None:
        """Fail fast when one of the required YAML files is absent."""
        self._write_valid_configuration()
        (self.config_directory / "prompts.yaml").unlink()

        with self.assertRaises(ConfigurationFileMissingError):
            ConfigurationManager(self.config_directory)

    def test_raises_for_invalid_yaml(self) -> None:
        """Raise a dedicated error when a YAML document cannot be parsed."""
        self._write_valid_configuration()
        (self.config_directory / "settings.yaml").write_text(
            "settings: [invalid", encoding="utf-8"
        )

        with self.assertRaises(ConfigurationParseError):
            ConfigurationManager(self.config_directory)

    def test_raises_for_a_non_mapping_yaml_root(self) -> None:
        """Reject a valid YAML document whose root is not a mapping."""
        self._write_valid_configuration()
        (self.config_directory / "prompts.yaml").write_text(
            "- resume\n- cover_letter\n", encoding="utf-8"
        )

        with self.assertRaises(ConfigurationParseError):
            ConfigurationManager(self.config_directory)

    def test_raises_for_an_empty_document(self) -> None:
        """Reject an empty required configuration document."""
        self._write_valid_configuration()
        (self.config_directory / "platforms.yaml").write_text("", encoding="utf-8")

        with self.assertRaises(EmptyConfigurationError):
            ConfigurationManager(self.config_directory)

    def test_preserves_exception_imports_from_config_module(self) -> None:
        """Keep the previous public exception imports available from core.config."""
        self.assertIs(ConfigurationError, SharedConfigurationError)

    def _write_valid_configuration(self) -> None:
        """Create a complete minimal configuration fixture."""
        documents = {
            "settings.yaml": "logging:\n  level: INFO\n",
            "user_profile.yaml": "skills:\n  - C#\n  - .NET\n",
            "platforms.yaml": "linkedin:\n  enabled: true\n",
            "prompts.yaml": "resume:\n  template: concise\n",
        }
        for file_name, contents in documents.items():
            (self.config_directory / file_name).write_text(contents, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
