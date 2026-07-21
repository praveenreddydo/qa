import re

from playwright.sync_api import Page, expect

from .config import TrupeerSettings


class LoginPage:
    def __init__(self, page: Page, settings: TrupeerSettings) -> None:
        self.page = page
        self.settings = settings

    @property
    def email_input(self):
        return self.page.locator('input[type="email"]')

    @property
    def password_input(self):
        return self.page.locator('input[type="password"]')

    @property
    def submit_button(self):
        return self.page.get_by_role("button", name="Sign in").or_(
            self.page.get_by_role("button", name="Log in")
        )

    def open(self) -> None:
        self.page.goto(f"{self.settings.base_url}{self.settings.login_path}", wait_until="domcontentloaded")
        expect(self.email_input, "The Trupeer sign-in email field should be visible.").to_be_visible()

    def login(self, email: str, password: str) -> None:
        self.open()
        self.email_input.fill(email)
        self.password_input.fill(password)
        expect(self.submit_button, "The sign-in button should be available after entering credentials.").to_be_enabled()
        self.submit_button.click()
        expect(self.page, "Successful sign-in should leave the login route.").not_to_have_url(
            re.compile(r"/login(?:[/?#]|$)")
        )
