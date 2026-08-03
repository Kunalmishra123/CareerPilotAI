"""Custom exceptions for the AI module."""


class AIError(Exception):
    """Base exception for AI-related errors."""


class AIConfigurationError(AIError):
    """Raised when AI configuration is invalid."""


class AIRequestError(AIError):
    """Raised when an AI request fails."""


class PromptNotFoundError(AIError):
    """Raised when a prompt template cannot be found."""