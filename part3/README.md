# Part 3 — AI-augmented testing

`python -m part3.validate` is an end-to-end validation runner that reuses the Part 2 Python Page Objects. It logs into Trupeer, captures the original generated script, sends four prompts to **Modify Script with AI**, and asks a separate LLM to judge every response against a structured rubric.

## Setup and run

From the repository root:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m part3.validate
```

Required `.env` values:

- Google sign-in: `TRUPEER_AUTH_MODE=google_session`, a session created with `python -m part2.bootstrap_google_session`, and `TRUPEER_VIDEO_URL`
- or direct sign-in: `TRUPEER_EMAIL`, `TRUPEER_PASSWORD`, and `TRUPEER_VIDEO_URL`
- `OPENAI_API_KEY`
- optional: `LLM_MODEL` (defaults to `gpt-4.1-mini`)
- optional: `LLM_JUDGE_MIN_CONFIDENCE` (defaults to `0.80`)

The command writes a timestamped JSON artifact under `part3/results/` and prints a concise pass/fail report. Use the artifact from a real run as `sample-output.json` before submitting; it includes all four prompts, AI outputs, per-criterion judgments, confidence, and the overall score.

For CI, use:

```bash
python -m part3.validate --fail-on-judge
```

This enables a non-zero exit code when any result fails the rubric or does not meet the configured confidence threshold. The runner reloads the editor before each prompt, preventing an uncommitted rewrite from accidentally becoming the next prompt's source.

## Rubric

The LLM returns parseable JSON for four criteria:

1. Does the output follow the user prompt?
2. Is it coherent and grammatically correct?
3. Does it preserve the original's core information?
4. Is it meaningfully different rather than a trivial rewording?

The judge uses temperature `0` to reduce variance. Its verdict is still advisory: it is a test signal, not proof that generated content is correct.
