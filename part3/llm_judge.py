from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class CriterionResult:
    name: str
    passed: bool
    confidence: float
    rationale: str


@dataclass(frozen=True)
class ScriptJudgment:
    overall_pass: bool
    confidence: float
    criteria: list[CriterionResult]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


JUDGE_PROMPT = """You are a strict but fair QA judge evaluating an AI rewrite of a video script.
Return only valid JSON in this exact shape:
{
  "overall_pass": true,
  "confidence": 0.0,
  "criteria": [
    {"name": "follows_prompt", "passed": true, "confidence": 0.0, "rationale": "short reason"},
    {"name": "coherent_and_grammatical", "passed": true, "confidence": 0.0, "rationale": "short reason"},
    {"name": "preserves_core_information", "passed": true, "confidence": 0.0, "rationale": "short reason"},
    {"name": "meaningfully_different", "passed": true, "confidence": 0.0, "rationale": "short reason"}
  ],
  "summary": "one short overall conclusion"
}

Rules:
- Use only the supplied text; do not invent details.
- For a translation prompt, judge grammar and instruction-following in the requested language.
- A concise rewrite may remove filler, but should retain the original's essential actions, claims, and ordering when relevant.
- Fail 'meaningfully_different' if the result merely changes a few words without serving the prompt.
- Set confidence between 0 and 1. Be conservative when the evidence is ambiguous.
"""


class LlmJudge:
    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY must be set in .env to run the Part 3 LLM judge.")
        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("LLM_MODEL", "gpt-4.1-mini")

    def evaluate(self, *, original_script: str, user_prompt: str, ai_output: str) -> ScriptJudgment:
        user_message = f"""Original script:
---
{original_script}
---

User instruction:
---
{user_prompt}
---

Trupeer AI output:
---
{ai_output}
---"""
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": JUDGE_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("The LLM judge returned an empty response.")
        return self._parse(content)

    @staticmethod
    def _parse(content: str) -> ScriptJudgment:
        try:
            payload = json.loads(content)
            criteria = [
                CriterionResult(
                    name=str(item["name"]),
                    passed=bool(item["passed"]),
                    confidence=LlmJudge._confidence(item["confidence"]),
                    rationale=str(item["rationale"]),
                )
                for item in payload["criteria"]
            ]
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"The LLM judge returned invalid structured JSON: {content}") from exc

        expected_names = {
            "follows_prompt",
            "coherent_and_grammatical",
            "preserves_core_information",
            "meaningfully_different",
        }
        received_names = {criterion.name for criterion in criteria}
        if received_names != expected_names:
            raise RuntimeError(f"LLM judge criteria were incomplete or unexpected: {received_names}")

        return ScriptJudgment(
            overall_pass=bool(payload["overall_pass"]),
            confidence=LlmJudge._confidence(payload["confidence"]),
            criteria=criteria,
            summary=str(payload["summary"]),
        )

    @staticmethod
    def _confidence(value: Any) -> float:
        confidence = float(value)
        if not 0 <= confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1.")
        return confidence

