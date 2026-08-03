"""Custom exceptions for browser automation workflows."""


class AutomationError(Exception):
    """Base exception for browser automation failures."""


class BrowserLaunchError(AutomationError):
    """Raised when the browser cannot be started."""


class ElementNotFoundError(AutomationError):
    """Raised when a requested page element is not available."""


class LoginError(AutomationError):
    """Raised when a login workflow fails."""


class SearchError(AutomationError):
    """Raised when a search workflow fails."""


class ApplicationError(AutomationError):
    """Raised when a job application workflow fails."""
