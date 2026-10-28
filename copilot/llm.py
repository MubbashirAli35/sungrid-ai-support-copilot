"""Thin Anthropic wrapper: structured outputs plus a running usage log for cost reporting."""
from functools import lru_cache
from typing import TypeVar

import anthropic
from pydantic import BaseModel

from copilot import config

T = TypeVar("T", bound=BaseModel)

USAGE: list[dict] = []


@lru_cache(maxsize=1)
def client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=config.anthropic_api_key())


def parse(model: str, system: str, user: str, output_format: type[T], purpose: str,
          effort: str = "low", max_tokens: int = 2000) -> T:
    """One call that must return JSON matching output_format. Raises on refusal or truncation."""
    response = client().messages.parse(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_format=output_format,
        output_config={"effort": effort},
    )
    USAGE.append({"purpose": purpose, "model": model,
                  "input_tokens": response.usage.input_tokens,
                  "output_tokens": response.usage.output_tokens})
    if response.parsed_output is None:
        raise ValueError(f"{purpose}: no parsed output (stop_reason={response.stop_reason})")
    return response.parsed_output


def cost_usd(usage: list[dict] | None = None) -> float:
    total = 0.0
    for u in USAGE if usage is None else usage:
        price_in, price_out = config.PRICES[u["model"]]
        total += (u["input_tokens"] * price_in + u["output_tokens"] * price_out) / 1_000_000
    return total
