"""Common page object helpers for browser automation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from playwright.sync_api import Locator, Page

from automation.exceptions import ElementNotFoundError
from automation.wait import WaitHelpers


class BasePage:
    """Provide reusable page-object operations."""

    def __init__(self, page: Page, wait_helpers: WaitHelpers | None = None) -> None:
        """Initialize the page wrapper."""
        self._page = page
        self._wait = wait_helpers if wait_helpers is not None else WaitHelpers(page)

    @property
    def page(self) -> Page:
        """Return the wrapped Playwright page."""
        return self._page

    def open(self, url: str) -> None:
        """Open a URL in the current page."""
        self._page.goto(url)

    def click(self, locator: str | Locator) -> None:
        """Click a locator after ensuring it is available."""
        self.wait(locator)
        self._resolve(locator).click()

    def fill(self, locator: str | Locator, text: str) -> None:
        """Fill a locator with text."""
        self.wait(locator)
        self._resolve(locator).fill(text)

    def wait(self, locator: str | Locator) -> Locator:
        """Wait until a locator becomes visible."""
        return self._wait.wait_for_visible(locator)

    def exists(self, locator: str | Locator) -> bool:
        """Return whether a locator exists on the current page."""
        resolved = self._resolve(locator)
        return resolved.count() > 0

    def text(self, locator: str | Locator) -> str:
        """Return the text content of a locator."""
        resolved = self._resolve(locator)
        if resolved.count() == 0:
            raise ElementNotFoundError(f"Element not found: {locator}")
        content = resolved.first.text_content()
        return content or ""

    def scroll(self, x: int = 0, y: int = 1000) -> None:
        """Scroll the page by the requested offset."""
        self._page.mouse.wheel(x, y)

    def press(self, locator: str | Locator, key: str) -> None:
        """Press a keyboard key on a locator."""
        self.wait(locator)
        self._resolve(locator).press(key)

    def select(self, locator: str | Locator, value: str | list[str]) -> None:
        """Select one or more values in a select element."""
        self.wait(locator)
        self._resolve(locator).select_option(value)

    def screenshot(self, path: str | Path, full_page: bool = True) -> None:
        """Capture a screenshot of the current page."""
        self._page.screenshot(path=str(path), full_page=full_page)

    def _resolve(self, locator: str | Locator) -> Locator:
        """Convert a locator expression into a Playwright locator."""
        if isinstance(locator, str):
            return self._page.locator(locator)
        return locator
