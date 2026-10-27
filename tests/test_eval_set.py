import re

from eval import scoring
from eval.scoring import DOLLAR_PATTERN, gate_respected, load_questions, recall_at_k, reciprocal_rank
from copilot.registry import load_registry

QS = load_questions()
Q = {q["id"]: q for q in QS}


def test_brief_coverage_requirements():
    reg = load_registry()
    assert 15 <= len(QS) <= 20
    covered = {q["expected_category"] for q in QS}
    assert covered == set(reg.categories) | {"non_relevant"}
    assert sum(q["type"] == "non_relevant" for q in QS) >= 2
    elig = [q for q in QS if q["type"] == "eligibility"]
    assert len(elig) >= 3 and any(q["expected_outcome"] == "ineligible" for q in elig)
    assert any(q["type"] == "ambiguous" for q in QS)


def test_gold_chunks_exist_in_the_corpus():
    from copilot.ingest import build_records
    keys = {f"{r['doc_id']}#{r['heading']}" for r in build_records()}
    for q in QS:
        for g in q.get("gold_chunks", []):
            assert g in keys, f"{q['id']}: unknown gold chunk {g}"


def test_eligibility_labels_agree_with_the_stub():
    import stub_tools
    for q in QS:
        if q["type"] == "eligibility" and q["expected_outcome"] in ("eligible", "ineligible"):
            p = q["expected_params"]
            r = stub_tools.check_rebate_eligibility(p["household_zip"], p["annual_income_usd"],
                                                    p["system_size_kw"], p["installer_approved"])
            assert r["eligible"] == (q["expected_outcome"] == "eligible"), q["id"]
            if r["eligible"]:
                assert r["estimated_rebate_usd"] == q["expected_rebate_usd"]


def test_retrieval_scorers():
    assert recall_at_k(["a", "b", "c"], ["c"], k=2) == 0.0
    assert recall_at_k(["a", "b", "c"], ["c"], k=3) == 1.0
    assert reciprocal_rank(["a", "b", "c"], ["b", "c"]) == 0.5


def test_dollar_guard_catches_figures_but_not_plain_text():
    assert DOLLAR_PATTERN.search("You would get $2,400")
    assert DOLLAR_PATTERN.search("about 2,400 dollars")
    assert not DOLLAR_PATTERN.search("Your income exceeds the regional threshold.")


def test_gate_scorer():
    denied = {"eligible": False, "reason": "x", "estimated_rebate_usd": 0.0}
    assert gate_respected("Not eligible: income too high.", True, denied, Q["q16"])
    assert not gate_respected("Not eligible, but roughly $3,000.", True, denied, Q["q16"])
    assert gate_respected("Please share your ZIP, income and installer status.", False, None, Q["q18"])
    assert not gate_respected("Probably around $2,800.", True, denied, Q["q18"])
