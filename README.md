# Trupeer QA Automation Assignment

An interview-ready Python QA automation project for the Trupeer QA Engineer assignment. It combines exploratory testing, maintainable browser automation, and LLM-augmented validation.

## Project map

| Folder | Deliverable |
| --- | --- |
| `part1/` | Exploratory-testing notes, recording link, and bug report |
| `part2/` | Python pytest-playwright end-to-end suite using Page Objects |
| `part3/` | LLM-judged validation of AI script modifications |
| `docs/` | PyCharm setup and interview walkthrough |

## Quick start

1. Install Python 3.10 or newer.
2. Copy `.env.example` to `.env` and fill in the Trupeer credentials, the video edit URL, and the LLM key.
3. Install the Python dependencies and Chromium browser:

    ```bash
    python -m pip install -r requirements.txt
    python -m playwright install chromium
    ```

4. Run the E2E suite:

    ```bash
    pytest part2
    ```

5. Run the AI-augmented validator:

    ```bash
    python -m part3.validate
    ```

