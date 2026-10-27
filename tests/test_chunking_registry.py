from copilot.chunking import chunk_markdown
from copilot.registry import load_registry

MD = "# Title\n\nIntro line.\n\n## A\nBody A.\n\n## B\n" + "\n\n".join(["word " * 100] * 3)


def test_intro_and_sections_become_chunks_with_context_prefix():
    chunks = chunk_markdown("x.md", MD)
    assert [c.heading for c in chunks][:2] == ["Overview", "A"]
    assert chunks[1].text.startswith("Title > A\n\n")


def test_long_section_splits_without_losing_text():
    chunks = [c for c in chunk_markdown("x.md", MD, max_words=150) if c.heading == "B"]
    assert len(chunks) == 3 and [c.part for c in chunks] == [0, 1, 2]


def test_registry_matches_docs_and_doc06_has_both_categories():
    reg = load_registry()
    assert len(reg.documents) == 14
    assert set(reg.documents["06_ambiguous_rebate_billing_adjustments.md"].categories) == {
        "incentive_rebate", "billing_account"}
    assert reg.documents["05_company_updates.md"].section_overrides["Upcoming Changes"].status == "unreleased"
