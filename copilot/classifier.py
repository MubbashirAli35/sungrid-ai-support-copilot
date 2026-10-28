"""Query classifier: one primary category, an optional secondary, and an intent."""
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from copilot import config, llm

PROMPT_PATH = Path(__file__).parent / "prompts" / "classifier_v1.md"

Category = Literal["program_policies", "incentive_rebate", "billing_account",
                   "technical_installation", "company_updates", "non_relevant"]
Topic = Literal["program_policies", "incentive_rebate", "billing_account",
                "technical_installation", "company_updates"]


class Classification(BaseModel):
    category: Category
    confidence: Literal["high", "medium", "low"]
    secondary_category: Topic | None
    intent: Literal["knowledge", "eligibility_check", "out_of_scope"]
    reasoning: str


def classify(question: str) -> Classification | None:
    """Returns None if the call fails or the output is inconsistent; the caller then
    searches without a category filter and never calls the eligibility tool."""
    try:
        result = llm.parse(config.RUNTIME_MODEL, PROMPT_PATH.read_text(), question,
                           Classification, purpose="classifier")
    except Exception:
        return None
    return result if is_consistent(result) else None


def is_consistent(c: Classification) -> bool:
    if c.category == "non_relevant":
        return c.intent == "out_of_scope" and c.secondary_category is None
    if c.intent == "out_of_scope":
        return False
    # Only the Rooftop Rebate has an eligibility checker.
    return c.intent != "eligibility_check" or c.category == "incentive_rebate"


def retrieval_filter(c: Classification | None) -> list[str] | None:
    """Categories to filter retrieval on. A secondary label is included unless the
    model was confident; None means search everywhere."""
    if c is None or c.category == "non_relevant":
        return None
    labels = [c.category]
    if c.secondary_category and c.confidence != "high":
        labels.append(c.secondary_category)
    return labels
