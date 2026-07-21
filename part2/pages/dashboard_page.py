import re

from playwright.sync_api import Page, expect

from .config import TrupeerSettings


class DashboardPage:
    def __init__(self, page: Page, settings: TrupeerSettings) -> None:
        self.page = page
        self.settings = settings

    @property
    def main_content(self):
        return self.page.get_by_role("main")

    def expect_loaded(self) -> None:
        expect(self.main_content, "The dashboard main content should be visible after login.").to_be_visible()
        expect(self.page, "The user should not still be on the sign-in route.").not_to_have_url(
            re.compile(r"/login(?:[/?#]|$)")
        )

    def open_recorded_video(self) -> None:
        """Navigate to the Part 1 recording without depending on card order."""
        if self.settings.video_url:
            self.page.goto(self.settings.video_url, wait_until="domcontentloaded")
            return

        if not self.settings.video_title:
            raise RuntimeError(
                "Set TRUPEER_VIDEO_URL (recommended) or TRUPEER_VIDEO_TITLE in .env so the suite can open the Part 1 video."
            )

        video_link = self.page.get_by_role("link", name=self.settings.video_title, exact=True)
        expect(video_link, f"The dashboard should contain the recorded video '{self.settings.video_title}'.").to_be_visible()
        video_link.click()
