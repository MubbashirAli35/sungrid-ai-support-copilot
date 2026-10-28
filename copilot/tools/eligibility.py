"""Eligibility path: extract inputs, validate, call the rebate service, answer from a template.

The LLM only reads the member's message into fields. It never decides eligibility and never
writes the reply: every outcome message is built here, and a dollar figure can only come from
the service's own `estimated_rebate_usd` when the service said eligible. Any failure on the
way (extraction, validation, the service call) ends in a no-figure message.
"""
import math
import re
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as CallTimeout
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from copilot import config, llm
from stub_tools import check_rebate_eligibility

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "extract_v1.md"
TOOL_TIMEOUT_S = 5.0
FIELDS = ("household_zip", "annual_income_usd", "system_size_kw", "installer_approved")
LABELS = {
    "household_zip": "your ZIP code",
    "annual_income_usd": "your household's annual income",
    "system_size_kw": "the planned system size in kW",
    "installer_approved": "whether your installer is on SunGrid's approved installer list",
}
DOLLAR = re.compile(r"\$\s?\d|\b\d[\d,]*(\.\d+)?\s?(dollars|usd)\b", re.IGNORECASE)
ZIP = re.compile(r"(\d{5})(-\d{4})?")


class Extraction(BaseModel):
    household_zip: str | None
    annual_income_usd: float | None
    system_size_kw: float | None
    installer_approved: bool | None


@dataclass
class Outcome:
    status: Literal["eligible", "ineligible", "needs_info", "error"]
    message: str
    params: dict = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    tool_called: bool = False
    tool_result: dict | None = None


def extract(question: str) -> dict:
    """Read the four inputs from the message; null where not stated."""
    return llm.parse(config.RUNTIME_MODEL, PROMPT_PATH.read_text(), question, Extraction,
                     purpose="extract").model_dump()


def validate(raw: dict) -> tuple[dict, list[str]]:
    """Keep only well-formed values; anything else counts as missing, so the member is asked.
    The service itself does no input checking (a negative size or a 9-digit ZIP just fails a check)."""
    params, missing = {}, []
    for name in FIELDS:
        value = raw.get(name)
        if name == "household_zip" and isinstance(value, str) and (m := ZIP.fullmatch(value.strip())):
            value = m.group(1)
        elif name == "annual_income_usd" and _number(value) and value >= 0:
            value = float(value)
        elif name == "system_size_kw" and _number(value) and value > 0:
            value = float(value)
        elif name == "installer_approved" and isinstance(value, bool):
            pass
        else:
            missing.append(name)
            continue
        params[name] = value
    return params, missing


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def call_service(params: dict) -> dict:
    """Call the service with a timeout. Raises on timeout or any error."""
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(check_rebate_eligibility, **params)
        try:
            return dict(future.result(timeout=TOOL_TIMEOUT_S))
        except CallTimeout as exc:
            raise TimeoutError("eligibility service timed out") from exc


def _safe_message(text: str) -> str:
    """Guard: a message for any outcome other than a confirmed rebate carries no dollar figure."""
    assert not DOLLAR.search(text), "dollar figure in a message that must have none"
    return text


def check(question: str) -> Outcome:
    try:
        params, missing = validate(extract(question))
    except Exception:
        return Outcome("error", _safe_message(
            "I couldn't read your details just now, so I can't check eligibility. "
            "Please try again, or contact SunGrid member support."))

    if missing:
        wanted = "; ".join(LABELS[m] for m in missing)
        return Outcome("needs_info", _safe_message(
            f"To check your eligibility I need a few more details: {wanted}. "
            "I can't estimate a rebate until I have them."), params, missing)

    try:
        result = call_service(params)
    except Exception:
        return Outcome("error", _safe_message(
            "The eligibility service isn't responding, so I can't check eligibility right now. "
            "Please try again later or contact SunGrid member support."), params, [], True)

    if result["eligible"] is True and result["estimated_rebate_usd"] > 0:
        return Outcome("eligible", (
            f"Based on the details you gave, you meet the Rooftop Rebate's eligibility checks. "
            f"The estimated rebate is ${result['estimated_rebate_usd']:,.2f}."), params, [], True, result)

    return Outcome("ineligible", _safe_message(
        f"You aren't eligible for the Rooftop Rebate: {result['reason']}"), params, [], True, result)
