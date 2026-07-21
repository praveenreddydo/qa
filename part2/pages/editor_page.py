from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from .config import TrupeerSettings


class EditorPage:
    """All editor locators are isolated here, keeping test behaviour selector-free."""

    def __init__(self, page: Page, settings: TrupeerSettings) -> None:
        self.page = page
        self.settings = settings

    @property
    def script_editor(self) -> Locator:
        return self.page.locator(self.settings.selector("TRUPEER_SCRIPT_SELECTOR", '[role="textbox"][aria-label*="Script" i]'))

    @property
    def preview(self) -> Locator:
        return self.page.locator(self.settings.selector("TRUPEER_PREVIEW_SELECTOR", "video"))

    @property
    def timeline(self) -> Locator:
        return self.page.locator(self.settings.selector("TRUPEER_TIMELINE_SELECTOR", 'text="Timeline"'))

    @property
    def ai_button(self) -> Locator:
        return self.page.locator(
            self.settings.selector("TRUPEER_AI_BUTTON_SELECTOR", 'button:has-text("Modify Script with AI")')
        )

    @property
    def ai_prompt_input(self) -> Locator:
        return self.page.locator(
            self.settings.selector("TRUPEER_AI_PROMPT_SELECTOR", '[role="textbox"][aria-label*="prompt" i]')
        )

    @property
    def ai_submit_button(self) -> Locator:
        return self.page.locator(
            self.settings.selector("TRUPEER_AI_SUBMIT_SELECTOR", 'button:has-text("Generate")')
        )

    @property
    def ai_result(self) -> Locator:
        return self.page.locator(self.settings.selector("TRUPEER_AI_RESULT_SELECTOR", '[role="textbox"][aria-label*="Script" i]'))

    @property
    def ai_validation_message(self) -> Locator:
        return self.page.locator(self.settings.selector("TRUPEER_AI_VALIDATION_SELECTOR", '[role="alert"]'))

    @property
    def zoom_in_button(self) -> Locator:
        return self.page.locator(self.settings.selector("TRUPEER_ZOOM_IN_SELECTOR", 'button[aria-label*="Zoom in" i]'))

    @property
    def zoom_value(self) -> Locator | None:
        selector = self.settings.selector("TRUPEER_ZOOM_VALUE_SELECTOR", "")
        return self.page.locator(selector) if selector else None

    def expect_loaded(self) -> None:
        expect(self.timeline, "The editor timeline should load.").to_be_visible()
        expect(self.preview, "The video preview should load.").to_be_visible()
        expect(self.script_editor, "The generated script editor should load.").to_be_visible()

    @staticmethod
    def _text_from(locator: Locator) -> str:
        return (locator.evaluate("""
            element => element instanceof HTMLTextAreaElement || element instanceof HTMLInputElement
                ? element.value
                : (element.textContent || '')
        """) or "").strip()

    def read_script(self) -> str:
        expect(self.script_editor, "The script field must be visible before reading it.").to_be_visible()
        return self._text_from(self.script_editor)

    def open_ai_modification(self) -> None:
        expect(self.ai_button, "The 'Modify Script with AI' control should be available.").to_be_visible()
        self.ai_button.click()
        expect(self.ai_prompt_input, "The AI instruction field should open.").to_be_visible()

    def modify_script(self, prompt: str, original_script: str) -> str:
        self.open_ai_modification()
        self.ai_prompt_input.fill(prompt)
        expect(self.ai_submit_button, "The AI modification request should be ready to submit.").to_be_enabled()
        self.ai_submit_button.click()
        expect(self.ai_result, "Trupeer should display a non-empty AI-modified script.").to_be_visible(timeout=60_000)

        tag_name = self.ai_result.evaluate("element => element.tagName")
        if tag_name in {"INPUT", "TEXTAREA"}:
            expect(self.ai_result, "The AI result should differ from the source script.").not_to_have_value(
                original_script, timeout=60_000
            )
        else:
            expect(self.ai_result, "The AI result should differ from the source script.").not_to_have_text(
                original_script, timeout=60_000
            )
        return self._text_from(self.ai_result)

    def submit_empty_ai_prompt(self) -> str:
        self.open_ai_modification()
        self.ai_prompt_input.fill("")
        if not self.ai_submit_button.is_enabled():
            return "blocked"

        self.ai_submit_button.click()
        expect(self.ai_validation_message, "An empty AI instruction should show validation feedback.").to_be_visible()
        return "validated"

    def zoom_in(self) -> None:
        if self.zoom_value is None:
            raise RuntimeError(
                "Set TRUPEER_ZOOM_VALUE_SELECTOR in .env so the zoom test can assert a state change rather than only a click."
            )

        before = self.zoom_value.get_attribute("aria-valuenow") or self.zoom_value.input_value()
        expect(self.zoom_in_button, "The editor zoom-in control should be available.").to_be_enabled()
        self.zoom_in_button.click()

        if self.zoom_value.get_attribute("aria-valuenow") is not None:
            expect(self.zoom_value, "Clicking zoom-in should change the editor zoom value.").not_to_have_attribute(
                "aria-valuenow", before
            )
        else:
            expect(self.zoom_value, "Clicking zoom-in should change the editor zoom value.").not_to_have_value(before)

