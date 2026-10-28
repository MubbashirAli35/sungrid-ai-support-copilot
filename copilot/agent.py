"""The copilot: classify, then take one of three paths.

  out of scope        -> fixed refusal, nothing is retrieved
  eligibility check   -> tools.eligibility (extract, validate, call the service, templated reply)
  knowledge           -> retrieve (soft category filter + fallback), then answer from the excerpts

Retrieval and the eligibility tool stay separate: the model never sees the tool, and the
knowledge path never produces a personal eligibility verdict or rebate figure.
"""
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

from copilot import classifier, config, llm
from copilot.retrieval import Hit, Retriever
from copilot.tools import eligibility

PROMPT_PATH = Path(__file__).parent / "prompts" / "answer_v1.md"
TOP_K = 5

OUT_OF_SCOPE = ("I can only help with SunGrid Cooperative questions: programs, rebates, billing, "
                "installation and company news. I can't help with that one.")
NOT_FOUND = ("I couldn't find that in the SunGrid knowledge base, so I don't want to guess. "
             "Please contact SunGrid member support.")


class Composed(BaseModel):
    answerable: bool
    answer: str
    cited: list[str]
    sources_disagree: bool


@dataclass
class Result:
    question: str
    path: str  # out_of_scope | eligibility | knowledge | abstain
    answer: str
    citations: list[str] = field(default_factory=list)
    classification: dict | None = None
    retrieval: dict | None = None
    eligibility: dict | None = None
    sources_disagree: bool = False
    seconds: float = 0.0
    cost_usd: float = 0.0


def format_context(hits: list[Hit]) -> str:
    parts = []
    for h in hits:
        flag = " (UNRELEASED: plan, not finalized)" if h.status == "unreleased" else ""
        parts.append(f"[{h.key}]{flag}\n{h.text}")
    return "\n\n".join(parts)


def compose(question: str, hits: list[Hit]) -> tuple[Composed | None, str]:
    """Answer from the excerpts. Returns (composed, note); composed is None when the answer
    must be replaced by the not-found message, and note says why."""
    user = f"Excerpts:\n\n{format_context(hits)}\n\nQuestion: {question}"
    try:
        out = llm.parse(config.RUNTIME_MODEL, PROMPT_PATH.read_text(), user, Composed, purpose="answer")
    except Exception as exc:
        return None, f"compose failed: {type(exc).__name__}"
    if not out.answerable:
        return None, "model said not answerable"
    retrieved = {h.key for h in hits}
    if not out.cited or not set(out.cited) <= retrieved:
        return None, "citations missing or not among the retrieved excerpts"
    return out, ""


class Copilot:
    def __init__(self, retriever: Retriever | None = None, trace: bool = True):
        self.retriever = retriever or Retriever()
        self.trace = trace

    def close(self):
        self.retriever.close()

    def ask(self, question: str) -> Result:
        start, usage_from = time.time(), len(llm.USAGE)
        c = classifier.classify(question)
        result = Result(question, "knowledge", "", classification=c.model_dump() if c else None)

        if c is not None and c.intent == "out_of_scope":
            result.path, result.answer = "out_of_scope", OUT_OF_SCOPE
        elif c is not None and c.intent == "eligibility_check":
            out = eligibility.check(question)
            result.path, result.answer = "eligibility", out.message
            result.eligibility = {"status": out.status, "params": out.params, "missing": out.missing,
                                  "tool_called": out.tool_called, "tool_result": out.tool_result}
        else:
            self._knowledge(result, c)

        result.seconds = round(time.time() - start, 2)
        result.cost_usd = round(llm.cost_usd(llm.USAGE[usage_from:]), 6)
        if self.trace:
            self._write_trace(result)
        return result

    def _knowledge(self, result: Result, c):
        found = self.retriever.search(result.question, classifier.retrieval_filter(c), k=TOP_K)
        result.retrieval = {"scope": found.scope, "fallback": found.fallback,
                            "hits": [{"key": h.key, "score": round(h.score, 4), "status": h.status}
                                     for h in found.hits]}
        composed, note = compose(result.question, found.hits)
        if composed is None:
            result.path, result.answer = "abstain", NOT_FOUND
            result.retrieval["abstain_reason"] = note
            return
        result.answer, result.citations = composed.answer, composed.cited
        result.sources_disagree = composed.sources_disagree

    def _write_trace(self, result: Result):
        config.TRACE_DIR.mkdir(exist_ok=True)
        record = {"time": datetime.now(timezone.utc).isoformat(), **asdict(result)}
        with open(config.TRACE_DIR / "traces.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
