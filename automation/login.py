"""Generic login workflow abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from automation.base_page import BasePage
from automation.exceptions import LoginError


class CredentialProvider(Protocol):
    """Provide username and password values for login workflows."""

    def get_username(self) -> str:
        """Return the username or email address."""

    def get_password(self) -> str:
        """Return the password."""


@dataclass(slots=True)
class LoginSelectors:
    """Generic selectors used by the login workflow."""

    username: str = (
        'input[type="email"], '
        'input[name="username"], '
        'input[name="email"]'
    )
    password: str = 'input[type="password"]'
    submit: str = 'button[type="submit"], input[type="submit"]'
    logout: str = (
        '[data-testid="logout"], '
        'a[href*="logout"], '
        'button:has-text("Logout")'
    )
    logged_in: str = (
        '[data-testid="user-menu"], '
        '[aria-label*="account"], '
        'nav'
    )


class LoginWorkflow:
    """Coordinate a generic login/logout workflow."""

    def __init__(
        self,
        base_page: BasePage,
        credential_provider: CredentialProvider,
        selectors: LoginSelectors | None = None,
    ) -> None:
        """Initialize the workflow with its dependencies."""
        self._page = base_page
        self._credentials = credential_provider
        self._selectors = selectors or LoginSelectors()

    def login(self) -> None:
        """Perform a generic login workflow."""
        try:
            self._page.fill(
                self._selectors.username,
                self._credentials.get_username(),
            )

            self._page.fill(
                self._selectors.password,
                self._credentials.get_password(),
            )

            self._page.click(self._selectors.submit)

            self._page.wait(self._selectors.logged_in)

            if not self.is_logged_in():
                raise LoginError(
                    "Login verification failed."
                )

        except Exception as error:
            self._page.screenshot(
                "screenshots/login_error.png"
            )
            raise LoginError(
                f"Login failed: {error}"
            ) from error

    def logout(self) -> None:
        """Perform a generic logout workflow."""
        try:
            self._page.click(self._selectors.logout)

            if self.is_logged_in():
                raise LoginError(
                    "Logout verification failed."
                )

        except Exception as error:
            self._page.screenshot(
                "screenshots/logout_error.png"
            )
            raise LoginError(
                f"Logout failed: {error}"
            ) from error

    def is_logged_in(self) -> bool:
        """Return whether the current session appears authenticated."""
        try:
            return self._page.exists(
                self._selectors.logged_in
            )
        except Exception:
            return False

    def ensure_logged_in(self) -> None:
        """Ensure the user is authenticated."""
        if not self.is_logged_in():
            raise LoginError(
                "User is not logged in."
            )