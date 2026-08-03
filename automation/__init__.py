"""Browser automation module for CareerPilot AI."""

from automation.apply import ApplicationWorkflow
from automation.base_page import BasePage
from automation.browser import BrowserManager, BrowserSettings
from automation.exceptions import (
    ApplicationError,
    AutomationError,
    BrowserLaunchError,
    ElementNotFoundError,
    LoginError,
    SearchError,
)
from automation.login import LoginWorkflow
from automation.search import SearchWorkflow
from automation.wait import WaitHelpers

__all__ = [
    "ApplicationError",
    "ApplicationWorkflow",
    "AutomationError",
    "BasePage",
    "BrowserLaunchError",
    "BrowserManager",
    "BrowserSettings",
    "ElementNotFoundError",
    "LoginError",
    "LoginWorkflow",
    "SearchError",
    "SearchWorkflow",
    "WaitHelpers",
]
