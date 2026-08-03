"""Unit tests for browser automation workflows."""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from pathlib import Path
import tempfile
from unittest.mock import MagicMock

from automation.apply import ApplicationWorkflow
from automation.base_page import BasePage
from automation.browser import BrowserManager, BrowserSettings
from automation.exceptions import (
    ApplicationError,
    BrowserLaunchError,
    ElementNotFoundError,
    LoginError,
    SearchError,
)
from automation.login import LoginSelectors, LoginWorkflow
from automation.search import SearchSelectors, SearchWorkflow
from automation.wait import WaitHelpers


@dataclass
class DummyCredentials:
    """Simple credential provider for tests."""

    username: str = "user@example.com"
    password: str = "secret"

    def get_username(self) -> str:
        return self.username

    def get_password(self) -> str:
        return self.password


class BrowserManagerTests(unittest.TestCase):
    """Verify browser lifecycle behavior."""

    def setUp(self) -> None:
        self.sync_playwright = MagicMock()
        self.playwright = MagicMock()
        self.browser_type = MagicMock()
        self.browser = MagicMock()
        self.playwright.chromium = self.browser_type
        self.browser_type.launch.return_value = self.browser
        self.sync_playwright.start.return_value = self.playwright

    def test_start_launches_browser(self) -> None:
        import automation.browser as browser_module

        browser_module.sync_playwright = MagicMock(return_value=self.sync_playwright)
        manager = BrowserManager(
            settings={
                "browser": {
                    "name": "chromium",
                    "headless": True,
                    "timeout_ms": 5000,
                    "navigation_timeout_ms": 7000,
                }
            }
        )

        result = manager.start()

        self.assertIs(result, self.browser)
        self.sync_playwright.start.assert_called_once()
        self.browser_type.launch.assert_called_once_with(headless=True)

    def test_new_context_sets_timeouts(self) -> None:
        import automation.browser as browser_module

        context = MagicMock()
        self.browser.new_context.return_value = context
        browser_module.sync_playwright = MagicMock(return_value=self.sync_playwright)

        manager = BrowserManager(
            settings={
                "browser": {
                    "name": "chromium",
                    "headless": True,
                    "timeout_ms": 30000,
                    "navigation_timeout_ms": 30000,
                    "viewport_width": 1440,
                    "viewport_height": 900,
                }
            }
        )
        manager._browser = self.browser

        result = manager.new_context()

        self.assertIs(result, context)
        context.set_default_timeout.assert_called_once_with(30000)
        context.set_default_navigation_timeout.assert_called_once_with(30000)

    def test_close_stops_resources(self) -> None:
        manager = BrowserManager(
            settings={
                "browser": {
                    "name": "chromium",
                    "headless": True,
                    "timeout_ms": 30000,
                    "navigation_timeout_ms": 30000,
                    "viewport_width": 1440,
                    "viewport_height": 900,
                }
            }
        )

        manager._browser = self.browser
        manager._playwright = self.playwright

        manager.close()

        self.browser.close.assert_called_once()
        self.playwright.stop.assert_called_once()

    def test_rejects_unsupported_browser(self) -> None:
        import automation.browser as browser_module

        browser_module.sync_playwright = MagicMock(return_value=self.sync_playwright)
        manager = BrowserManager(
            settings={
                "browser": {
                    "name": "edge",
                }
            }
        )

        with self.assertRaises(BrowserLaunchError):
            manager.start()


class BasePageTests(unittest.TestCase):
    """Verify common page helpers."""

    def setUp(self) -> None:
        self.page = MagicMock()
        self.locator = MagicMock()
        self.page.locator.return_value = self.locator
        self.locator.count.return_value = 1
        self.locator.text_content.return_value = "Hello"
        self.wait_helpers = MagicMock(spec=WaitHelpers)
        self.wait_helpers.wait_for_visible.return_value = self.locator
        self.base_page = BasePage(self.page, wait_helpers=self.wait_helpers)

    def test_open_calls_goto(self) -> None:
        self.base_page.open("https://example.com")
        self.page.goto.assert_called_once_with("https://example.com")

    def test_click_uses_wait_helper(self) -> None:
        self.base_page.click("#submit")
        self.wait_helpers.wait_for_visible.assert_called_once_with("#submit")
        self.locator.click.assert_called_once()

    def test_text_raises_when_missing(self) -> None:
        self.locator.count.return_value = 0
        with self.assertRaises(ElementNotFoundError):
            self.base_page.text("#missing")

    def test_scroll_and_screenshot(self) -> None:
        self.base_page.scroll(10, 20)
        self.base_page.screenshot(Path("shot.png"))
        self.page.mouse.wheel.assert_called_once_with(10, 20)
        self.page.screenshot.assert_called_once()


class WaitHelpersTests(unittest.TestCase):
    """Verify wait helper behavior."""

    def setUp(self) -> None:
        self.page = MagicMock()
        self.locator = MagicMock()
        self.page.locator.return_value = self.locator
        self.locator.count.return_value = 1
        self.locator.first = self.locator
        self.wait = WaitHelpers(self.page)

    def test_wait_for_visible_returns_locator(self) -> None:
        result = self.wait.wait_for_visible("#id")
        self.assertIs(result, self.locator)

    def test_wait_for_hidden_raises_when_missing(self) -> None:
        self.locator.count.return_value = 0
        with self.assertRaises(ElementNotFoundError):
            self.wait.wait_for_hidden("#id")

    def test_wait_for_network_idle(self) -> None:
        self.wait.wait_for_network_idle()
        self.page.wait_for_load_state.assert_called_once_with("networkidle")


class LoginWorkflowTests(unittest.TestCase):
    """Verify generic login workflow behavior."""

    def setUp(self) -> None:
        self.base_page = MagicMock(spec=BasePage)
        self.workflow = LoginWorkflow(
            self.base_page,
            DummyCredentials(),
            selectors=LoginSelectors(),
        )

    def test_login_fills_credentials_and_submits(self) -> None:
        self.workflow.login()
        self.base_page.fill.assert_any_call(
            self.workflow._selectors.username,
            "user@example.com",
        )
        self.base_page.fill.assert_any_call(
            self.workflow._selectors.password,
            "secret",
        )
        self.base_page.click.assert_called_once_with(self.workflow._selectors.submit)

    def test_is_logged_in_uses_exists(self) -> None:
        self.base_page.exists.return_value = True
        self.assertTrue(self.workflow.is_logged_in())

    def test_logout_wraps_errors(self) -> None:
        self.base_page.click.side_effect = RuntimeError("boom")
        with self.assertRaises(LoginError):
            self.workflow.logout()


class SearchWorkflowTests(unittest.TestCase):
    """Verify generic search workflow behavior."""

    def setUp(self) -> None:
        self.base_page = MagicMock(spec=BasePage)
        self.workflow = SearchWorkflow(self.base_page, selectors=SearchSelectors())

    def test_search_jobs_uses_enter(self) -> None:
        self.workflow.search_jobs("python")
        self.base_page.fill.assert_called_once()
        self.base_page.press.assert_called_once()

    def test_next_page_returns_false_when_absent(self) -> None:
        self.base_page.exists.return_value = False
        self.assertFalse(self.workflow.next_page())

    def test_apply_filters_wraps_errors(self) -> None:
        self.base_page.click.side_effect = RuntimeError("boom")
        with self.assertRaises(SearchError):
            self.workflow.apply_filters({"role": "engineer"})


class ApplicationWorkflowTests(unittest.TestCase):
    """Verify generic application workflow behavior."""

    def setUp(self) -> None:
        self.page = MagicMock(spec=BasePage)
        self.workflow = ApplicationWorkflow(self.page)

    def test_start_application_clicks_start_button(self) -> None:
        self.workflow.start_application()
        self.page.click.assert_called_once()

    def test_upload_resume_sets_input_files(self) -> None:
        self.page.page = MagicMock()

        with tempfile.NamedTemporaryFile(suffix=".pdf") as resume:
            self.workflow.upload_resume(Path(resume.name))

        self.page.page.set_input_files.assert_called_once()

    def test_submit_application_wraps_errors(self) -> None:
        self.page.click.side_effect = RuntimeError("boom")
        with self.assertRaises(ApplicationError):
            self.workflow.submit_application()


if __name__ == "__main__":
    unittest.main()
