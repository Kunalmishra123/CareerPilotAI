"""Reusable wait helpers for Playwright pages."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from automation.exceptions import ElementNotFoundError


class WaitHelpers:
    """Provide explicit, reusable wait operations."""

    def __init__(self, page: Page) -> None:
        """Initialize the helper with a Playwright page."""
        self._page = page

    def wait_for_visible(self, locator: str | Locator) -> Locator:
        """Wait until a locator is visible and return it."""
        element = self._get_locator(locator)
        element.wait_for(state="visible")
        return element

    def wait_for_hidden(self, locator: str | Locator) -> Locator:
        """Wait until a locator is hidden and return it."""
        element = self._get_locator(locator)
        element.wait_for(state="hidden")
        return element

    def wait_for_network_idle(self) -> None:
        """Wait until network activity has completed."""
        self._page.wait_for_load_state("networkidle")

    def wait_for_page_load(self) -> None:
        """Wait until the page has fully loaded."""
        self._page.wait_for_load_state("domcontentloaded")
        self._page.wait_for_load_state("load")

    def wait_until_enabled(self, locator: str | Locator) -> Locator:
        """Wait until a locator becomes enabled."""
        element = self._get_locator(locator)
        element.wait_for(state="visible")

        self._page.wait_for_function(
            "(element) => !element.disabled",
            arg=element,
        )

        return element

    def wait_for_timeout(self, milliseconds: int) -> None:
        """Wait for a fixed amount of time."""
        self._page.wait_for_timeout(milliseconds)

    def wait_for_url(self, url: str) -> None:
        """Wait until the page navigates to the specified URL."""
        self._page.wait_for_url(url)

    def _get_locator(self, locator: str | Locator) -> Locator:
        """Resolve and validate a locator."""
        element = self._resolve(locator).first

        if element.count() == 0:
            raise ElementNotFoundError(
                f"Element not found: {locator}"
            )

        return element

    def _resolve(self, locator: str | Locator) -> Locator:
        """Convert a locator expression into a Playwright locator."""
        if isinstance(locator, str):
            return self._page.locator(locator)
        return locator