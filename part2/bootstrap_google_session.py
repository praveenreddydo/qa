"""Create a local Playwright session after a one-time manual Google sign-in in Chrome.

Run from the repository root:
    python -m part2.bootstrap_google_session
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, sync_playwright

from part2.pages import DashboardPage, TrupeerSettings


def find_chrome(settings: TrupeerSettings) -> Path:
    """Find a normal local Chrome installation; it is not launched through Playwright."""
    candidates = [
        settings.chrome_path,
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise RuntimeError(
        "Google Chrome was not found. Set TRUPEER_CHROME_PATH in .env to the full path to chrome.exe."
    )


def dashboard_page(context: BrowserContext, settings: TrupeerSettings) -> Page:
    matching_pages = [page for page in context.pages if page.url.startswith(settings.base_url)]
    if matching_pages:
        return matching_pages[-1]
    return context.new_page()


def main() -> None:
    settings = TrupeerSettings.from_environment()
    if not settings.uses_google_session:
        raise RuntimeError("Set TRUPEER_AUTH_MODE=google_session in .env before running this command.")

    settings.storage_state.parent.mkdir(parents=True, exist_ok=True)
    chrome_profile = settings.storage_state.parent / "chrome-profile"
    chrome = find_chrome(settings)

    subprocess.Popen(
        [
            str(chrome),
            "--remote-debugging-port=9222",
            f"--user-data-dir={chrome_profile}",
            "--no-first-run",
            f"{settings.base_url}{settings.login_path}",
        ]
    )

    print("A normal Chrome window is open. Select Google and complete your sign-in there.")
    input("When Trupeer's dashboard is visible, return here and press Enter to save the local test session: ")

    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(settings.cdp_url)
        if not browser.contexts:
            raise RuntimeError("Chrome did not expose a browser context. Close Chrome and run the command again.")
        context = browser.contexts[0]
        page = dashboard_page(context, settings)
        if not page.url.startswith(settings.base_url):
            page.goto(settings.base_url, wait_until="domcontentloaded")
        dashboard = DashboardPage(page, settings)
        dashboard.expect_loaded()
        context.storage_state(path=str(settings.storage_state))

    print(f"Saved local Google test session to: {settings.storage_state}")
    print("This session and its dedicated Chrome profile are ignored by Git. Re-run this command if the session expires.")


if __name__ == "__main__":
    main()
