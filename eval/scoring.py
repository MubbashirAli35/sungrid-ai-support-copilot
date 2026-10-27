"""Deterministic scorers. No LLM calls; every function is a pure check."""
import re
from pathlib import Path

import yaml

QUESTIONS_PATH = Path(__file__).resolve().parent / "questions.yaml"

# A denied or incomplete eligibility answer must contain no dollar figure at all.
DOLLAR_PATTERN = re.compile(r"\$\s?\d|\b\d[\d,]*(\.\d+)?\s?(dollars|usd)\b", re.IGNORECASE)


def load_questions(path: Path = QUESTIONS_PATH) -> list[dict]:
    return yaml.safe_load(path.read_text())["questions"]


def chunk_key(doc_id: str, heading: str) -> str:
    return f"{doc_id}#{heading}"


def recall_at_k(retrieved: list[str], gold: list[str], k: int = 5) -> float:
    """1.0 if any gold chunk is in the top k, else 0.0."""
    return 1.0 if set(retrieved[:k]) & set(gold) else 0.0


def reciprocal_rank(retrieved: list[str], gold: list[str]) -> float:
    for rank, key in enumerate(retrieved, start=1):
        if key in gold:
            return 1.0 / rank
    return 0.0


def category_correct(predicted: str, question: dict) -> bool:
    return predicted in question.get("acceptable_categories", [question["expected_category"]])


def intent_correct(predicted: str, question: dict) -> bool:
    return predicted == question["expected_intent"]


def params_correct(extracted: dict, question: dict) -> bool:
    """Every expected parameter must match exactly; extra extracted fields must be null."""
    expected = question.get("expected_params", {})
    for name, value in expected.items():
        if extracted.get(name) != value:
            return False
    return all(v is None for k, v in extracted.items() if k not in expected)


def gate_respected(answer: str, tool_called: bool, tool_result: dict | None, question: dict) -> bool:
    """The hard gate: unless the service said eligible, the answer has no figure and
    the outcome matches the expected one."""
    outcome = question["expected_outcome"]
    if outcome == "needs_clarification":
        return not tool_called and not DOLLAR_PATTERN.search(answer)
    if not tool_called or tool_result is None:
        return False
    if outcome == "ineligible":
        return tool_result["eligible"] is False and not DOLLAR_PATTERN.search(answer)
    return tool_result["eligible"] is True and tool_result["estimated_rebate_usd"] == question["expected_rebate_usd"]
