from copilot.classifier import Classification, is_consistent, retrieval_filter


def make(**kw):
    base = dict(category="incentive_rebate", confidence="high", secondary_category=None,
                intent="knowledge", reasoning="x")
    return Classification(**{**base, **kw})


def test_non_relevant_must_be_out_of_scope():
    assert is_consistent(make(category="non_relevant", intent="out_of_scope"))
    assert not is_consistent(make(category="non_relevant", intent="knowledge"))
    assert not is_consistent(make(category="billing_account", intent="out_of_scope"))


def test_eligibility_intent_only_valid_for_rebate_category():
    assert is_consistent(make(intent="eligibility_check"))
    assert not is_consistent(make(category="billing_account", intent="eligibility_check"))


def test_filter_includes_secondary_unless_confident():
    assert retrieval_filter(make(secondary_category="billing_account")) == ["incentive_rebate"]
    assert retrieval_filter(make(confidence="medium", secondary_category="billing_account")) == [
        "incentive_rebate", "billing_account"]


def test_filter_is_none_when_unsure_or_irrelevant():
    assert retrieval_filter(None) is None
    assert retrieval_filter(make(category="non_relevant", intent="out_of_scope")) is None
