from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from part2.pages import DashboardPage, EditorPage, LoginPage, TrupeerSettings
from part3.llm_judge import LlmJudge, ScriptJudgment


DEFAULT_PROMPTS = [
    "Make this script more professional while preserving the original information.",
    "Add a clear call to action at the end.",
    "Translate this script to Spanish.",
    "Make this script more concise while retaining the essential steps.",
]
RESULTS_DIR = Path(__file__).resolve().parent / "results"


@dataclass(frozen=True)
class PromptResult:
    prompt: str
    ai_output: str
    judgment: ScriptJudgment

    @property
    def passed(self) -> bool:
        return self.judgment.overall_pass and all(item.passed for item in self.judgment.criteria)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Trupeer AI script modifications with an LLM judge.")
    parser.add_argument(
        "--fail-on-judge",
        action="store_true",
        help="Exit 1 if any prompt fails the rubric or the configured confidence threshold.",
    )
    return parser.parse_args()


def validate() -> tuple[list[PromptResult], float, str]:
    settings = TrupeerSettings.from_environment()
    email, password = settings.require_credentials() if not settings.uses_google_session else (None, None)
    judge = LlmJudge()
    headless = os.getenv("HEADLESS", "true").lower() != "false"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(
            **({"storage_state": str(settings.require_storage_state())} if settings.uses_google_session else {})
        )
        page = context.new_page()
        login_page = LoginPage(page, settings)
        dashboard_page = DashboardPage(page, settings)
        editor_page = EditorPage(page, settings)

        if settings.uses_google_session:
            page.goto(settings.base_url, wait_until="domcontentloaded")
        else:
            login_page.login(email or "", password or "")
        dashboard_page.expect_loaded()
        dashboard_page.open_recorded_video()
        editor_page.expect_loaded()
        original_script = editor_page.read_script()
        if not original_script:
            raise RuntimeError("The selected Part 1 video has no generated script to validate.")

        results: list[PromptResult] = []
        for prompt in DEFAULT_PROMPTS:
            # Re-open the editor before each prompt so accidental unsaved UI state does not chain rewrites.
            page.reload(wait_until="domcontentloaded")
            editor_page.expect_loaded()
            ai_output = editor_page.modify_script(prompt, original_script)
            judgment = judge.evaluate(
                original_script=original_script,
                user_prompt=prompt,
                ai_output=ai_output,
            )
            results.append(PromptResult(prompt=prompt, ai_output=ai_output, judgment=judgment))

        browser.close()

    return results, float(os.getenv("LLM_JUDGE_MIN_CONFIDENCE", "0.80")), original_script


def write_results(results: list[PromptResult], threshold: float, original_script: str) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_path = RESULTS_DIR / f"validation-{timestamp}.json"
    passed = [result.passed and result.judgment.confidence >= threshold for result in results]
    payload = {
        "run_at_utc": timestamp,
        "model": os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        "confidence_threshold": threshold,
        "original_script": original_script,
        "overall_score": sum(passed) / len(passed),
        "ci_gate_passed": all(passed),
        "results": [
            {
                "prompt": result.prompt,
                "ai_output": result.ai_output,
                "passed": result.passed,
                "judgment": asdict(result.judgment),
            }
            for result in results
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def print_summary(results: list[PromptResult], threshold: float, output_path: Path) -> bool:
    gate_results = []
    print("\nAI-augmented validation results")
    print(f"Confidence threshold: {threshold:.0%}\n")
    for result in results:
        gate_passed = result.passed and result.judgment.confidence >= threshold
        gate_results.append(gate_passed)
        status = "PASS" if gate_passed else "FAIL"
        print(f"{status} | {result.prompt}")
        print(f"  Judge confidence: {result.judgment.confidence:.0%} — {result.judgment.summary}")
        for criterion in result.judgment.criteria:
            criterion_status = "PASS" if criterion.passed else "FAIL"
            print(f"  - {criterion_status}: {criterion.name} ({criterion.confidence:.0%})")

    score = sum(gate_results) / len(gate_results)
    print(f"\nOverall score: {score:.0%} ({sum(gate_results)}/{len(gate_results)} prompts passed)")
    print(f"Full JSON results: {output_path}")
    return all(gate_results)


def main() -> int:
    args = parse_args()
    results, threshold, original_script = validate()
    output_path = write_results(results, threshold, original_script)
    passed = print_summary(results, threshold, output_path)
    return 0 if passed or not args.fail_on_judge else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"Validation could not complete: {exc}", file=sys.stderr)
        sys.exit(2)
