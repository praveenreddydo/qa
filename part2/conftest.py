from __future__ import annotations

from collections.abc import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from part2.pages import DashboardPage, EditorPage, LoginPage, TrupeerSettings


@pytest.fixture(scope="session")
def trupeer_settings() -> TrupeerSettings:
    return TrupeerSettings.from_environment()


@pytest.fixture
def app_page(
    page: Page, browser: Browser, trupeer_settings: TrupeerSettings
) -> Generator[Page, None, None]:
    """Use Playwright's normal page for password auth or a saved session for Google OAuth."""
    if not trupeer_settings.uses_google_session:
        yield page
        return

    context: BrowserContext = browser.new_context(
        storage_state=str(trupeer_settings.require_storage_state())
    )
    google_page = context.new_page()
    yield google_page
    context.close()


@pytest.fixture
def login_page(app_page: Page, trupeer_settings: TrupeerSettings) -> LoginPage:
    return LoginPage(app_page, trupeer_settings)


@pytest.fixture
def dashboard_page(app_page: Page, trupeer_settings: TrupeerSettings) -> DashboardPage:
    return DashboardPage(app_page, trupeer_settings)


@pytest.fixture
def editor_page(app_page: Page, trupeer_settings: TrupeerSettings) -> EditorPage:
    return EditorPage(app_page, trupeer_settings)


@pytest.fixture
def authenticated_dashboard(
    login_page: LoginPage,
    dashboard_page: DashboardPage,
    trupeer_settings: TrupeerSettings,
) -> DashboardPage:
    if trupeer_settings.uses_google_session:
        dashboard_page.page.goto(trupeer_settings.base_url, wait_until="domcontentloaded")
    else:
        email, password = trupeer_settings.require_credentials()
        login_page.login(email, password)
    dashboard_page.expect_loaded()
    return dashboard_page


@pytest.fixture
def opened_editor(authenticated_dashboard: DashboardPage, editor_page: EditorPage) -> EditorPage:
    authenticated_dashboard.open_recorded_video()
    editor_page.expect_loaded()
    return editor_page


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    settings = TrupeerSettings.from_environment()
    if settings.uses_google_session or settings.has_credentials:
        return

    marker = pytest.mark.skip(
        reason="Configure Google session auth or set TRUPEER_EMAIL and TRUPEER_PASSWORD in .env to run live Trupeer tests."
    )
    for item in items:
        item.add_marker(marker)
