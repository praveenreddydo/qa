# Part 2 — Python pytest-playwright E2E tests

## Coverage

- Login and dashboard landing
- Open the Part 1 recorded video and verify timeline, preview, and script surfaces
- Modify the generated script with AI and verify a changed, non-empty result
- Negative validation for an empty AI prompt
- Zoom-in editor interaction

Selectors are isolated in `pages/`. `EditorPage` supports semantic selectors first and optional environment overrides for any labels or DOM structure that differ in the live Trupeer UI. This keeps the test logic stable while preserving a small, explicit calibration surface.

## Setup

From the repository root:

```bash
copy .env.example .env
python -m pip install -r requirements.txt
python -m playwright install chromium
pytest part2
```

Set these in `.env`:

- `TRUPEER_AUTH_MODE=google_session` — recommended for a Google-sign-in Trupeer account
- `TRUPEER_STORAGE_STATE=part2/.auth/trupeer_google_session.json` — local test session location
- `TRUPEER_VIDEO_URL` — preferred: direct editor URL for the microphone-enabled Part 1 video
- `TRUPEER_VIDEO_TITLE` — only needed when no direct video URL is supplied

## Google sign-in setup

Do not put your Google password in `.env`. After filling in `.env`, run:

```bash
python -m part2.bootstrap_google_session
```

A visible Playwright browser opens. Complete the Google sign-in yourself, wait until the Trupeer dashboard appears, then return to the terminal and press Enter. The script writes a local browser session file to `part2/.auth/`, which is ignored by Git. Re-run it whenever the session expires.

Google may block automated browser windows as insecure. The bootstrap command therefore opens normal Google Chrome for this one-time login, then connects only to save the local Trupeer test session. It never asks for or stores your Google password. If Chrome is installed outside its normal Windows location, set `TRUPEER_CHROME_PATH` in `.env`.

For a separate email/password test account, set `TRUPEER_AUTH_MODE=password`, `TRUPEER_EMAIL`, and `TRUPEER_PASSWORD` instead.

If the live UI does not expose the semantic labels assumed by the Page Object, set only the needed overrides below after inspecting the target element. Do not add selectors directly to tests.

```dotenv
TRUPEER_SCRIPT_SELECTOR=
TRUPEER_PREVIEW_SELECTOR=
TRUPEER_TIMELINE_SELECTOR=
TRUPEER_AI_BUTTON_SELECTOR=
TRUPEER_AI_PROMPT_SELECTOR=
TRUPEER_AI_SUBMIT_SELECTOR=
TRUPEER_AI_RESULT_SELECTOR=
TRUPEER_AI_VALIDATION_SELECTOR=
TRUPEER_ZOOM_IN_SELECTOR=
TRUPEER_ZOOM_VALUE_SELECTOR=
```

Run headed for calibration:

```bash
pytest part2 --headed
```

The suite deliberately uses assertion and URL waits rather than fixed delays. On failure, pytest-playwright retains trace, screenshot, and video evidence.
