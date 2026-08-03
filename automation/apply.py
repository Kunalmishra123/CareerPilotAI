"""Generic job application workflow abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from automation.base_page import BasePage
from automation.exceptions import ApplicationError


@dataclass(slots=True)
class ApplicationSelectors:
    """Generic selectors used by the application workflow."""

    start_button: str = (
        'button:has-text("Apply"), '
        'a:has-text("Apply")'
    )

    resume_upload: str = (
        'input[type="file"][name*="resume"], '
        'input[type="file"]'
    )

    cover_letter_upload: str = (
        'input[type="file"][name*="cover"], '
        'input[type="file"]'
    )

    submit_button: str = (
        'button[type="submit"], '
        'button:has-text("Submit")'
    )


class ApplicationWorkflow:
    """Coordinate generic application submission actions."""

    def __init__(
        self,
        base_page: BasePage,
        selectors: ApplicationSelectors | None = None,
    ) -> None:
        """Initialize the workflow."""
        self._page = base_page
        self._selectors = selectors or ApplicationSelectors()

    def start_application(self) -> None:
        """Start a generic application workflow."""
        try:
            self._page.click(
                self._selectors.start_button
            )

            self._page.wait(
                self._selectors.resume_upload
            )

        except Exception as error:
            self._page.screenshot(
                "screenshots/application_start_error.png"
            )
            raise ApplicationError(
                f"Starting application failed: {error}"
            ) from error

    def upload_resume(
        self,
        resume_path: str | Path,
    ) -> None:
        """Upload a resume file."""
        try:
            resume_path = Path(resume_path)

            if not resume_path.exists():
                raise ApplicationError(
                    f"Resume not found: {resume_path}"
                )

            self._page.page.set_input_files(
                self._selectors.resume_upload,
                str(resume_path),
            )

        except Exception as error:
            self._page.screenshot(
                "screenshots/resume_upload_error.png"
            )
            raise ApplicationError(
                f"Uploading resume failed: {error}"
            ) from error

    def upload_cover_letter(
        self,
        cover_letter_path: str | Path,
    ) -> None:
        """Upload a cover letter."""
        try:
            cover_letter_path = Path(
                cover_letter_path
            )

            if not cover_letter_path.exists():
                raise ApplicationError(
                    f"Cover letter not found: "
                    f"{cover_letter_path}"
                )

            self._page.page.set_input_files(
                self._selectors.cover_letter_upload,
                str(cover_letter_path),
            )

        except Exception as error:
            self._page.screenshot(
                "screenshots/cover_letter_upload_error.png"
            )
            raise ApplicationError(
                f"Uploading cover letter failed: {error}"
            ) from error

    def submit_application(self) -> None:
        """Submit the application."""
        try:
            self._page.click(
                self._selectors.submit_button
            )

            self._page.page.wait_for_load_state(
                "networkidle"
            )

        except Exception as error:
            self._page.screenshot(
                "screenshots/application_submit_error.png"
            )
            raise ApplicationError(
                f"Submitting application failed: {error}"
            ) from error