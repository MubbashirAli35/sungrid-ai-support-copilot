"""Eval runner.
  python -m eval.run_eval retrieval   scores retrieval (no LLM calls) -> eval/reports/retrieval.md
  python -m eval.run_eval classifier  scores the LLM classifier, 3 runs -> eval/reports/classifier.md"""
import argparse
import datetime
from pathlib import Path

from copilot.registry import load_registry
from copilot.retrieval import Retriever
from eval.scoring import category_correct, intent_correct, load_questions, recall_at_k, reciprocal_rank

REPORT = Path(__file__).resolve().parent / "reports" / "retrieval.md"
CLASSIFIER_REPORT = REPORT.with_name("classifier.md")
RUNS = 3


def wrong_label(question: dict, categories: list[str]) -> str:
    """Simulate a classifier mistake: the next category that is not an acceptable answer."""
    ok = question.get("acceptable_categories", [question["expected_category"]])
    i = categories.index(question["expected_category"])
    for step in range(1, len(categories)):
        candidate = categories[(i + step) % len(categories)]
        if candidate not in ok:
            return candidate


def score(retriever, questions, mode: dict, categories: list[str]) -> dict:
    r1 = r3 = r5 = mrr = 0.0
    misses = []
    for q in questions:
        label = {"none": None, "correct": [q["expected_category"]],
                 "wrong": [wrong_label(q, categories)]}[mode["label"]]
        result = retriever.search(q["question"], label, k=5, hybrid=mode["hybrid"],
                                  fallback_margin=mode["margin"])
        keys = [h.key for h in result.hits]
        r1 += recall_at_k(keys, q["gold_chunks"], 1)
        r3 += recall_at_k(keys, q["gold_chunks"], 3)
        hit5 = recall_at_k(keys, q["gold_chunks"], 5)
        r5 += hit5
        mrr += reciprocal_rank(keys, q["gold_chunks"])
        if not hit5:
            misses.append(q["id"])
    n = len(questions)
    return {"r1": r1 / n, "r3": r3 / n, "r5": r5 / n, "mrr": mrr / n, "misses": misses}


def run_retrieval():
    categories = load_registry().categories
    questions = [q for q in load_questions() if q.get("gold_chunks")]
    retriever = Retriever()
    from copilot import config
    m = config.FALLBACK_MARGIN
    modes = [
        ("Dense, no category filter", dict(label="none", hybrid=False, margin=None)),
        ("Dense + BM25 (RRF), no category filter", dict(label="none", hybrid=True, margin=None)),
        ("Dense, correct label, strict filter", dict(label="correct", hybrid=False, margin=None)),
        ("Dense + BM25, correct label, strict filter", dict(label="correct", hybrid=True, margin=None)),
        ("Dense, correct label, with fallback", dict(label="correct", hybrid=False, margin=m)),
        ("Dense, WRONG label, strict filter", dict(label="wrong", hybrid=False, margin=None)),
        ("Dense, WRONG label, with fallback", dict(label="wrong", hybrid=False, margin=m)),
    ]
    rows = []
    for name, mode in modes:
        s = score(retriever, questions, mode, categories)
        rows.append(f"| {name} | {s['r1']:.2f} | {s['r3']:.2f} | {s['r5']:.2f} | {s['mrr']:.2f} | "
                    f"{', '.join(s['misses']) or '-'} |")

    amb = [q for q in questions if q["type"] == "ambiguous"]
    amb_rows = []
    for q in amb:
        for cat in q["acceptable_categories"]:
            res = retriever.search(q["question"], [cat], k=5, fallback_margin=None)
            keys = [h.key for h in res.hits]
            amb_rows.append(f"| {q['id']} | {cat} | {recall_at_k(keys, q['gold_chunks'], 1):.0f} | "
                            f"{recall_at_k(keys, q['gold_chunks'], 5):.0f} |")
    retriever.close()

    lines = [
        "# Retrieval results",
        f"Generated {datetime.date.today()} by `python -m eval.run_eval retrieval`. "
        f"{len(questions)} questions with gold chunks, corpus of 69 chunks, bge-small-en-v1.5, "
        f"fallback margin {m}.",
        "",
        "| Mode | recall@1 | recall@3 | recall@5 | MRR | questions missed at 5 |",
        "|---|---|---|---|---|---|",
        *rows,
        "",
        "Ambiguous doc 06, strict filter on each acceptable label:",
        "",
        "| question | label | hit@1 | hit@5 |",
        "|---|---|---|---|",
        *amb_rows,
        "",
        "Caveats: n is small, and the 69-chunk corpus makes recall@5 easy (5 chunks is 7% of the "
        "corpus). The fallback margin was chosen after looking at the score gaps on these same "
        "questions, so the fallback rows are optimistic.",
    ]
    REPORT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def run_classifier():
    from copilot import classifier, llm
    questions = load_questions()
    runs = []
    for _ in range(RUNS):
        runs.append({q["id"]: classifier.classify(q["question"]) for q in questions})

    def covered(c, q):
        """Ambiguous questions pass if both defensible labels appear in category/secondary."""
        return c is not None and set(q["acceptable_categories"]) <= {c.category, c.secondary_category}

    rows, cat_ok, int_ok, stable = [], 0, 0, 0
    for q in questions:
        preds = [r[q["id"]] for r in runs]
        cats = [bool(c) and category_correct(c.category, q) for c in preds]
        ints = [bool(c) and intent_correct(c.intent, q) for c in preds]
        cat_ok += sum(cats)
        int_ok += sum(ints)
        stable += len({(c.category, c.intent) if c else None for c in preds}) == 1
        seen = "; ".join(f"{c.category}/{c.confidence}/{c.intent}" if c else "None" for c in preds)
        flag = "" if all(cats) and all(ints) else " **MISS**"
        sec = ""
        if q["type"] == "ambiguous":
            sec = f" both labels covered: {sum(covered(c, q) for c in preds)}/{RUNS}."
        rows.append(f"| {q['id']} | {q['expected_category']} / {q['expected_intent']} | {seen} |{flag}{sec} |")

    n = len(questions) * RUNS
    in_scope = [q for q in questions if q["type"] != "non_relevant"]
    cost = llm.cost_usd()
    lines = [
        "# Classifier results",
        f"Generated {datetime.date.today()} by `python -m eval.run_eval classifier`. "
        f"Model {llm.config.RUNTIME_MODEL}, prompt classifier_v1, {len(questions)} questions x {RUNS} runs.",
        "",
        f"- Category accuracy: {cat_ok}/{n} ({cat_ok / n:.0%})",
        f"- Intent accuracy: {int_ok}/{n} ({int_ok / n:.0%})",
        f"- Questions with identical output in all {RUNS} runs: {stable}/{len(questions)}",
        f"- Cost of this run: ${cost:.4f} for {len(llm.USAGE)} calls "
        f"(${cost / len(llm.USAGE) * 1000:.2f} per 1,000 classifier calls)",
        "",
        "| id | expected category / intent | predicted per run (category/confidence/intent) | note |",
        "|---|---|---|---|",
        *rows,
        "",
        "Caveats: 20 questions, written by the same person who wrote the prompt. The prompt contains "
        "no eval questions as examples, but its category definitions were written after reading the docs. "
        "Sampling parameters cannot be fixed on this model, so runs differ.",
    ]
    CLASSIFIER_REPORT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", choices=["retrieval", "classifier"])
    args = parser.parse_args()
    {"retrieval": run_retrieval, "classifier": run_classifier}[args.suite]()
