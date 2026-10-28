import pytest

from copilot.tools import eligibility
from copilot.tools.eligibility import Outcome, check, validate

GOOD = dict(household_zip="94103", annual_income_usd=85000, system_size_kw=6.0, installer_approved=True)


def fake_extract(monkeypatch, **fields):
    base = {name: None for name in eligibility.FIELDS}
    monkeypatch.setattr(eligibility, "extract", lambda q: {**base, **fields})


def test_eligible_uses_service_figure(monkeypatch):
    fake_extract(monkeypatch, **GOOD)
    out = check("q")
    assert out.status == "eligible" and "$2,400.00" in out.message and out.tool_called


@pytest.mark.parametrize("change,reason", [
    (dict(annual_income_usd=135000), "income"),
    (dict(household_zip="90210"), "ZIP"),
    (dict(installer_approved=False), "Installer"),
    (dict(system_size_kw=12.0), "System size"),
    (dict(annual_income_usd=120000), "income"),  # the boundary fails
])
def test_failed_check_gets_reason_and_no_figure(monkeypatch, change, reason):
    fake_extract(monkeypatch, **{**GOOD, **change})
    out = check("q")
    assert out.status == "ineligible" and reason in out.message
    assert not eligibility.DOLLAR.search(out.message)


def test_missing_fields_ask_and_never_call_the_service(monkeypatch):
    fake_extract(monkeypatch, system_size_kw=7.0)
    monkeypatch.setattr(eligibility, "call_service", lambda p: pytest.fail("service must not be called"))
    out = check("q")
    assert out.status == "needs_info" and not out.tool_called
    assert out.missing == ["household_zip", "annual_income_usd", "installer_approved"]
    assert not eligibility.DOLLAR.search(out.message)


def test_unsure_installer_is_missing_not_false(monkeypatch):
    fake_extract(monkeypatch, **{**GOOD, "installer_approved": None})
    assert check("q").missing == ["installer_approved"]


def test_service_failure_fails_closed(monkeypatch):
    fake_extract(monkeypatch, **GOOD)
    def boom(params): raise RuntimeError("down")
    monkeypatch.setattr(eligibility, "check_rebate_eligibility", boom)
    out = check("q")
    assert out.status == "error" and not eligibility.DOLLAR.search(out.message)


def test_service_timeout_fails_closed(monkeypatch):
    import time
    fake_extract(monkeypatch, **GOOD)
    monkeypatch.setattr(eligibility, "TOOL_TIMEOUT_S", 0.05)
    monkeypatch.setattr(eligibility, "check_rebate_eligibility", lambda **p: time.sleep(0.3))
    assert check("q").status == "error"


def test_extraction_failure_fails_closed(monkeypatch):
    def boom(q): raise ValueError("no parse")
    monkeypatch.setattr(eligibility, "extract", boom)
    out = check("q")
    assert out.status == "error" and not out.tool_called


def test_service_saying_eligible_with_zero_rebate_is_not_trusted(monkeypatch):
    fake_extract(monkeypatch, **GOOD)
    monkeypatch.setattr(eligibility, "call_service",
                        lambda p: {"eligible": True, "reason": "x", "estimated_rebate_usd": 0.0})
    assert check("q").status == "ineligible"


def test_validate_rejects_malformed_values():
    params, missing = validate(dict(household_zip="9410", annual_income_usd=-5,
                                    system_size_kw=float("nan"), installer_approved="yes"))
    assert params == {} and len(missing) == 4
    assert validate({**GOOD, "household_zip": "94103-1234"})[0]["household_zip"] == "94103"
    assert validate({**GOOD, "system_size_kw": 0})[1] == ["system_size_kw"]
