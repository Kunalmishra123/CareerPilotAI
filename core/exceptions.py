"""Custom exceptions for CareerPilot AI application infrastructure."""


class ConfigurationError(Exception):
    """Base exception raised when application configuration cannot be loaded."""


class ConfigurationFileMissingError(ConfigurationError):
    """Raised when a required configuration file does not exist."""


class ConfigurationParseError(ConfigurationError):
    """Raised when a configuration file contains invalid YAML."""


class EmptyConfigurationError(ConfigurationError):
    """Raised when a required configuration file has no usable content."""
