import pytest
from qdrant_client import QdrantClient

from copilot.ingest import ingest
from copilot.retrieval import Retriever


@pytest.fixture(scope="module")
def retriever(tmp_path_factory):
    client = QdrantClient(path=str(tmp_path_factory.mktemp("qdrant")))
    ingest(client)
    r = Retriever(client)
    yield r
    r.close()


def keys(result):
    return [h.key for h in result.hits]


def test_correct_filter_keeps_only_that_category(retriever):
    res = retriever.search("What does fault code E07 mean?", ["technical_installation"], fallback_margin=None)
    assert all("technical_installation" in h.categories for h in res.hits)
    assert keys(res)[0] == "04#Common Fault Codes"


def test_wrong_filter_without_fallback_misses_the_answer(retriever):
    res = retriever.search("What does fault code E07 mean?", ["company_updates"], fallback_margin=None)
    assert "04#Common Fault Codes" not in keys(res)


def test_wrong_filter_with_fallback_recovers_and_reports_it(retriever):
    res = retriever.search("What does fault code E07 mean?", ["company_updates"])
    assert res.fallback and res.scope == "unfiltered"
    assert "04#Common Fault Codes" in keys(res)


def test_right_filter_does_not_trigger_fallback(retriever):
    res = retriever.search("What does fault code E07 mean?", ["technical_installation"])
    assert not res.fallback and res.scope == "filtered"


def test_doc06_is_found_under_either_label(retriever):
    q = "My rebate was reversed after I received it. How will SunGrid recover the money?"
    for label in ("incentive_rebate", "billing_account"):
        assert "06#Reversal Process" in keys(retriever.search(q, [label], fallback_margin=None))


def test_unreleased_status_reaches_the_caller(retriever):
    top = retriever.search("Is a fourth membership tier coming?").hits[0]
    assert top.key == "05#Upcoming Changes" and top.status == "unreleased"


def test_hybrid_returns_ranked_hits_with_fused_scores(retriever):
    res = retriever.search("fault code E07", hybrid=True)
    assert res.hits[0].key == "04#Common Fault Codes"
    assert res.hits[0].score > res.hits[-1].score
