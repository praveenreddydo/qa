import re

import pytest
from playwright.sync_api import expect

from part2.pages import DashboardPage, LoginPage, TrupeerSettings


@pytest.mark.e2e
def test_registered_user_can_log_in_and_reach_dashboard(
    login_page: LoginPage,
    dashboard_page: DashboardPage,
    trupeer_settings: TrupeerSettings,
) -> None:
    if trupeer_settings.uses_google_session:
        login_page.page.goto(trupeer_settings.base_url, wait_until="domcontentloaded")
    else:
        email, password = trupeer_settings.require_credentials()
        login_page.login(email, password)
    dashboard_page.expect_loaded()
    expect(dashboard_page.page, "The authenticated page should not be the sign-in page.").not_to_have_url(
        re.compile(r"/login(?:[/?#]|$)")
    )
