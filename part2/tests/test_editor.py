import pytest

from part2.pages import EditorPage


@pytest.mark.e2e
def test_recorded_video_editor_loads_key_editing_surfaces(opened_editor: EditorPage) -> None:
    opened_editor.expect_loaded()


@pytest.mark.e2e
def test_modify_script_with_ai_returns_a_changed_script(opened_editor: EditorPage) -> None:
    original = opened_editor.read_script()
    assert original, "The Part 1 recording must have a non-empty generated script."

    modified = opened_editor.modify_script(
        "Make this script more concise while preserving its key steps.", original
    )

    assert modified, "The returned AI script should contain content."
    assert modified != original, "The returned AI script should not exactly equal the source script."


@pytest.mark.e2e
def test_empty_modify_script_prompt_is_rejected(opened_editor: EditorPage) -> None:
    outcome = opened_editor.submit_empty_ai_prompt()
    assert outcome in {"blocked", "validated"}, (
        "The UI should disable submission or show validation feedback for an empty prompt."
    )


@pytest.mark.e2e
def test_zoom_in_changes_editor_zoom_state(opened_editor: EditorPage) -> None:
    opened_editor.zoom_in()

