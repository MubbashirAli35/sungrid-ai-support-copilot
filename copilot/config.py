"""Settings read from the environment. No secrets live in code."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
REGISTRY_PATH = ROOT / "data" / "doc_registry.yaml"
QDRANT_PATH = ROOT / "qdrant_data"
COLLECTION = "sungrid_kb"
TRACE_DIR = ROOT / "traces"

FALLBACK_MARGIN = 0.05  # provisional; see eval/reports for how it was chosen
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RUNTIME_MODEL = os.getenv("COPILOT_RUNTIME_MODEL", "claude-haiku-5-5")
JUDGE_MODEL = os.getenv("COPILOT_JUDGE_MODEL", "claude-sonnet-5-5")


def anthropic_api_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set; copy .env.example to .env")
    return key


# USD per 1M tokens (input, output), from Anthropic list prices for prompts up to 100K tokens.
PRICES = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
}
