# Interview walkthrough: Trupeer QA Automation Assignment

## One-minute overview

This is a Python QA project with three layers. Part 1 establishes product understanding through exploratory testing and evidence-based bugs. Part 2 automates the highest-value user flows with pytest-playwright. Part 3 handles the non-deterministic AI rewrite feature by using a separate LLM as a structured quality judge rather than asserting an exact string.

## Architecture

```text
part2/tests/        Test intent: login, editor, AI rewrite, negative case, zoom
        │
        ▼
part2/pages/        Page Objects: selectors and browser actions
        │
        ▼
Trupeer UI          Live test account and Part 1 recorded video

part3/validate.py   Reuses the same Page Objects
        │
        ├── captures original + AI-modified scripts
        └── part3/llm_judge.py evaluates structured quality criteria
```

## Key decisions to explain

### Why pytest-playwright?

Python keeps the suite accessible, pytest gives clear fixtures and assertions, and Playwright provides reliable browser waiting, traces, screenshots, and video evidence.

### Why Page Objects?

Tests describe business intent; `part2/pages/` owns element location and interactions. A UI selector change is therefore corrected in one place instead of across every test.

### Why configuration through `.env`?

Video URLs, API keys, and any live selector adjustments vary by environment. Keeping them out of source control protects secrets and makes the suite portable. Google OAuth is handled through a one-time local session bootstrap instead of storing a Google password.

### How do you reduce test flakiness?

The suite uses Playwright expectations and URL/state waits, not arbitrary sleeps. It opens a known recorded-video URL rather than relying on dashboard ordering, and stores trace, screenshot, and video artifacts on failure.

### Why an LLM judge for Part 3?

AI rewrites are intentionally non-deterministic. Exact text matching would be brittle and not meaningful. The judge evaluates prompt-following, coherence, information preservation, and meaningful change, returning parseable JSON with confidence per criterion.

## Honest limitations and next steps

- Live selectors must be calibrated once against the actual authenticated editor; selector overrides are intentionally isolated in `.env`.
- The LLM judge is a quality signal, not a replacement for human review. Low-confidence or disputed results should be warnings until calibrated against human labels.
- For CI at scale, I would retain session storage after a tested login flow, use a dedicated test account, and record judge disagreements to improve the rubric.

## Demo order

1. Show Part 1’s recording link and two strongest functional bugs.
2. Run the login and editor tests in headed mode.
3. Open `EditorPage` to show selector separation.
4. Run Part 3 and open its generated JSON result.
5. Explain the 80% initial confidence threshold and human-review fallback.
