"""Generic job search workflow abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from automation.base_page import BasePage
from automation.exceptions import SearchError


@dataclass(slots=True)
class SearchSelectors:
    """Generic selectors used by the search workflow."""

    search_input: str = (
        'input[type="search"], '
        'input[name="q"], '
        'input[placeholder*="Search"]'
    )

    filter_button: str = (
        'button:has-text("Filter"), '
        'button:has-text("Filters")'
    )

    job_card: str = (
        '[data-testid="job-card"], '
        'article, '
        'li'
    )

    next_page: str = (
        'a[rel="next"], '
        'button:has-text("Next")'
    )

    job_link: str = (
        'a[href*="/jobs/"], '
        'a[href*="/job/"], '
        'a:has-text("View job")'
    )


class SearchWorkflow:
    """Coordinate generic job search actions."""

    def __init__(
        self,
        base_page: BasePage,
        selectors: SearchSelectors | None = None,
    ) -> None:
        """Initialize the workflow."""
        self._page = base_page
        self._selectors = selectors or SearchSelectors()

    def search_jobs(self, query: str) -> None:
        """Search for jobs."""
        try:
            self._page.fill(
                self._selectors.search_input,
                query,
            )

            self._page.press(
                self._selectors.search_input,
                "Enter",
            )

            self._page.wait(self._selectors.job_card)

        except Exception as error:
            self._page.screenshot(
                "screenshots/search_error.png"
            )
            raise SearchError(
                f"Job search failed: {error}"
            ) from error

    def apply_filters(
        self,
        filters: dict[str, Any] | None = None,
    ) -> None:
        """Apply search filters."""
        try:
            if not filters:
                return

            self._page.click(
                self._selectors.filter_button
            )

            self._page.wait(
                self._selectors.job_card
            )

        except Exception as error:
            self._page.screenshot(
                "screenshots/filter_error.png"
            )
            raise SearchError(
                f"Applying filters failed: {error}"
            ) from error

    def open_job(self) -> None:
        """Open the selected job."""
        try:
            self._page.click(
                self._selectors.job_link
            )

            self._page.wait(self._selectors.job_link)

        except Exception as error:
            self._page.screenshot(
                "screenshots/open_job_error.png"
            )
            raise SearchError(
                f"Opening job failed: {error}"
            ) from error

    def next_page(self) -> bool:
        """Navigate to the next page of results."""
        try:
            if not self._page.exists(
                self._selectors.next_page
            ):
                return False

            self._page.click(
                self._selectors.next_page
            )

            self._page.wait(
                self._selectors.job_card
            )

            return True

        except Exception as error:
            self._page.screenshot(
                "screenshots/paging_error.png"
            )
            raise SearchError(
                f"Paging failed: {error}"
            ) from error