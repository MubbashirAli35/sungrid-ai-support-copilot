import pytest

from copilot import agent
from copilot.agent import Composed, Copilot
from copilot.classifier import Classification
from copilot.retrieval import Hit, SearchResult
from copilot.tools import eligibility


def hit(key, status="published"):
    return Hit(key, "doc", key.split("#")[1], f"text of {key}", 0.8, ["program_policies"], status)


class FakeRetriever:
    def __init__(self, hits):
        self.hits, self.seen = hits, None

    def search(self, query, categories=None, k=5, **kw):
        self.seen = categories
        return SearchResult(self.hits, "filtered" if categories else "unfiltered")

    def close(self):
        pass


def cls(**kw):
    base = dict(category="program_policies", confidence="high", secondary_category=None,
                intent="knowledge", reasoning="x")
    return Classification(**{**base, **kw})


def make(monkeypatch, classification, hits=(), composed=None):
    monkeypatch.setattr(agent.classifier, "classify", lambda q: classification)
    monkeypatch.setattr(agent.llm, "parse", lambda *a, **k: composed)
    return Copilot(FakeRetriever(list(hits)), trace=False)


def test_out_of_scope_retrieves_nothing(monkeypatch):
    bot = make(monkeypatch, cls(category="non_relevant", intent="out_of_scope"))
    r = bot.ask("weather?")
    assert r.path == "out_of_scope" and r.retrieval is None


def test_knowledge_answer_keeps_valid_citations(monkeypatch):
    composed = Composed(answerable=True, answer="Once a year.", cited=["01#Tier Transfers"], sources_disagree=False)
    bot = make(monkeypatch, cls(), [hit("01#Tier Transfers")], composed)
    r = bot.ask("q")
    assert r.path == "knowledge" and r.citations == ["01#Tier Transfers"]


def test_citation_not_in_retrieved_set_abstains(monkeypatch):
    composed = Composed(answerable=True, answer="x", cited=["99#Invented"], sources_disagree=False)
    r = make(monkeypatch, cls(), [hit("01#Tier Transfers")], composed).ask("q")
    assert r.path == "abstain" and r.answer == agent.NOT_FOUND


def test_answer_without_citation_abstains(monkeypatch):
    composed = Composed(answerable=True, answer="x", cited=[], sources_disagree=False)
    assert make(monkeypatch, cls(), [hit("01#Tier Transfers")], composed).ask("q").path == "abstain"


def test_model_says_not_answerable_abstains(monkeypatch):
    composed = Composed(answerable=False, answer="", cited=[], sources_disagree=False)
    assert make(monkeypatch, cls(), [hit("01#Tier Transfers")], composed).ask("q").path == "abstain"


def test_compose_failure_abstains(monkeypatch):
    bot = make(monkeypatch, cls(), [hit("01#Tier Transfers")])
    monkeypatch.setattr(agent.llm, "parse", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("api down")))
    assert bot.ask("q").path == "abstain"


def test_classifier_failure_searches_everywhere_and_never_calls_the_tool(monkeypatch):
    monkeypatch.setattr(eligibility, "check", lambda q: pytest.fail("tool must not run"))
    composed = Composed(answerable=True, answer="a", cited=["01#Tier Transfers"], sources_disagree=False)
    bot = make(monkeypatch, None, [hit("01#Tier Transfers")], composed)
    r = bot.ask("q")
    assert bot.retriever.seen is None and r.path == "knowledge"


def test_eligibility_intent_uses_the_tool_not_retrieval(monkeypatch):
    out = eligibility.Outcome("needs_info", "need more", {}, ["household_zip"])
    monkeypatch.setattr(eligibility, "check", lambda q: out)
    bot = make(monkeypatch, cls(category="incentive_rebate", intent="eligibility_check"))
    r = bot.ask("am I eligible?")
    assert r.path == "eligibility" and r.answer == "need more" and r.retrieval is None


def test_unreleased_chunks_are_labelled_in_the_prompt_context():
    ctx = agent.format_context([hit("05#Upcoming Changes", "unreleased"), hit("01#Tier Transfers")])
    assert "[05#Upcoming Changes] (UNRELEASED" in ctx and "[01#Tier Transfers]\n" in ctx


def test_bracketed_citation_ids_are_normalised_but_still_checked(monkeypatch):
    ok = Composed(answerable=True, answer="a", cited=["[01#Tier Transfers]"], sources_disagree=False)
    assert make(monkeypatch, cls(), [hit("01#Tier Transfers")], ok).ask("q").citations == ["01#Tier Transfers"]
    bad = Composed(answerable=True, answer="a", cited=["[99#Invented]"], sources_disagree=False)
    assert make(monkeypatch, cls(), [hit("01#Tier Transfers")], bad).ask("q").path == "abstain"
