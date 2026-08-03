"""Playwright browser lifecycle management for CareerPilot AI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from automation.exceptions import BrowserLaunchError
from core.config import ConfigurationManager
from core.logger import get_logger


DEFAULT_BROWSER_NAME = "chromium"
DEFAULT_HEADLESS = True
DEFAULT_TIMEOUT_MS = 30000
DEFAULT_NAVIGATION_TIMEOUT_MS = 30000
DEFAULT_VIEWPORT_WIDTH = 1440
DEFAULT_VIEWPORT_HEIGHT = 900


@dataclass(frozen=True, slots=True)
class BrowserSettings:
    """Resolved browser settings used to launch Playwright."""

    browser_name: str = DEFAULT_BROWSER_NAME
    headless: bool = DEFAULT_HEADLESS
    timeout_ms: int = DEFAULT_TIMEOUT_MS
    navigation_timeout_ms: int = DEFAULT_NAVIGATION_TIMEOUT_MS
    viewport_width: int = DEFAULT_VIEWPORT_WIDTH
    viewport_height: int = DEFAULT_VIEWPORT_HEIGHT


class BrowserManager:
    """Manage Playwright browser, contexts, and pages."""

    def __init__(
        self,
        settings: Mapping[str, Any] | BrowserSettings | None = None,
    ) -> None:
        """Initialize the manager from configuration or explicit settings."""
        self._logger = get_logger()
        self._settings = self._resolve_settings(settings)
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._contexts: list[BrowserContext] = []
        self._current_context: BrowserContext | None = None
        self._current_page: Page | None = None

    @property
    def browser(self) -> Browser | None:
        """Return the active browser instance, if one has been launched."""
        return self._browser

    @property
    def playwright(self) -> Playwright | None:
        """Return the active Playwright runtime, if one has been started."""
        return self._playwright

    @property
    def settings(self) -> BrowserSettings:
        """Return the resolved browser settings."""
        return self._settings

    def __enter__(self) -> "BrowserManager":
        """Enter context manager."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        self.close()

    def start(self) -> Browser:
        """Start Playwright and launch the configured browser."""
        if self._browser is not None:
            return self._browser

        try:
            self._playwright = sync_playwright().start()
            browser_type = self._get_browser_type()
            launch_options = {
                "headless": self._settings.headless,
            }
            self._browser = browser_type.launch(**launch_options)
            self._logger.info("Browser launched using {}", self._settings.browser_name)
            return self._browser
        except Exception as error:
            self.close()
            raise BrowserLaunchError(f"Unable to launch browser: {error}") from error

    def new_context(self) -> BrowserContext:
        """Create a new browser context with configured timeouts and viewport."""
        browser = self.start()
        context = browser.new_context(
            viewport={
                "width": self._settings.viewport_width,
                "height": self._settings.viewport_height,
            }
        )
        self._contexts.append(context)
        self._current_context = context
        context.set_default_timeout(self._settings.timeout_ms)
        context.set_default_navigation_timeout(self._settings.navigation_timeout_ms)
        return context

    def new_page(
        self,
        context: BrowserContext | None = None,
    ) -> Page:
        """Create a new page in a fresh browser context."""
        context = context or self.new_context()
        page = context.new_page()
        self._current_page = page
        return page

    def close(self) -> None:
        """Close the browser and Playwright runtime if they are active."""
        if self._browser is not None:
            for context in self._contexts.copy():
                self.close_context(context)
            self._contexts.clear()
            self._current_context = None
            self._current_page = None
            self._browser.close()
            self._browser = None
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def close_context(self, context: BrowserContext) -> None:
        """Close a browser context."""
        try:
            context.close()
        finally:
            if context in self._contexts:
                self._contexts.remove(context)

    def close_page(self, page: Page) -> None:
        """Close a browser page."""
        page.close()

        if self._current_page is page:
            self._current_page = None

    def take_screenshot(self, path: str) -> None:
        """Capture a screenshot of the current page."""
        if self._current_page is not None:
            self._current_page.screenshot(path=path)

    def _get_browser_type(self) -> Any:
        """Return the configured Playwright browser type."""
        if self._playwright is None:
            raise BrowserLaunchError("Playwright has not been started.")

        browser_name = self._settings.browser_name.lower().strip()
        mapping = {
            "chromium": self._playwright.chromium,
            "firefox": self._playwright.firefox,
            "webkit": self._playwright.webkit,
        }

        if browser_name not in mapping:
            raise BrowserLaunchError(
                f"Unsupported browser '{browser_name}'."
            )

        return mapping[browser_name]

    @classmethod
    def _resolve_settings(
        cls,
        settings: Mapping[str, Any] | BrowserSettings | None,
    ) -> BrowserSettings:
        """Build browser settings from configuration or explicit overrides."""

        if isinstance(settings, BrowserSettings):
            return settings

        if settings is None:
            settings = cls._load_settings()

        browser_settings = settings.get("browser", settings)

        if not isinstance(browser_settings, Mapping):
            browser_settings = {}

        return BrowserSettings(
            browser_name=cls._get_text(
                browser_settings,
                "name",
                DEFAULT_BROWSER_NAME,
            ),
            headless=cls._get_bool(
                browser_settings,
                "headless",
                DEFAULT_HEADLESS,
            ),
            timeout_ms=cls._get_int(
                browser_settings,
                "timeout_ms",
                DEFAULT_TIMEOUT_MS,
            ),
            navigation_timeout_ms=cls._get_int(
                browser_settings,
                "navigation_timeout_ms",
                DEFAULT_NAVIGATION_TIMEOUT_MS,
            ),
            viewport_width=cls._get_int(
                browser_settings,
                "viewport_width",
                DEFAULT_VIEWPORT_WIDTH,
            ),
            viewport_height=cls._get_int(
                browser_settings,
                "viewport_height",
                DEFAULT_VIEWPORT_HEIGHT,
            ),
        )

    @staticmethod
    def _load_settings() -> Mapping[str, Any]:
        """Load browser settings from the application configuration."""
        try:
            settings = ConfigurationManager().get_settings()
        except Exception:
            return {}
        return settings if isinstance(settings, Mapping) else {}

    @staticmethod
    def _get_text(settings: Mapping[str, Any], name: str, default: str) -> str:
        value = settings.get(name, default)
        return value.strip() if isinstance(value, str) and value.strip() else default

    @staticmethod
    def _get_bool(settings: Mapping[str, Any], name: str, default: bool) -> bool:
        value = settings.get(name, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "on"}:
                return True
            if normalized in {"false", "0", "no", "off"}:
                return False
        return default

    @staticmethod
    def _get_int(settings: Mapping[str, Any], name: str, default: int) -> int:
        value = settings.get(name, default)
        return value if isinstance(value, int) and value > 0 else default
