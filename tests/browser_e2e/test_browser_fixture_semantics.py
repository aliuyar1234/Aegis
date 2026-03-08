from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    return yaml.safe_load((ROOT / "tests/browser_e2e/fixtures" / name).read_text())


def test_effectful_fixtures_align_with_policy_defaults_and_tool_catalog():
    billing = _load("effectful_billing_address_update.yaml")
    uncertain = _load("uncertain_submit_recovery.yaml")
    entitlement = _load("effectful_entitlement_revoke.yaml")

    assert billing["requires_approval"] is True
    assert billing["tool_id"] == "browser.submit"
    assert billing["risk_class"] == "browser_write"
    assert billing["expected_policy_decision"] == "require_approval"

    assert uncertain["requires_approval"] is True
    assert uncertain["tool_id"] == "browser.submit"
    assert uncertain["risk_class"] == "browser_write"
    assert uncertain["expected_policy_decision"] == "require_approval"

    assert entitlement["requires_approval"] is False
    assert entitlement["tool_id"] == "browser.delete"
    assert entitlement["risk_class"] == "browser_write"
    assert entitlement["expected_policy_decision"] == "deny"


def test_read_only_fixtures_do_not_require_approval():
    for name in ["read_only_account_lookup.yaml", "read_only_billing_inspection.yaml"]:
        payload = _load(name)
        assert payload["requires_approval"] is False
        assert payload["expected_policy_decision"] == "allow"
        assert payload["mutation_class"] == "read_only"
        assert all(step["kind"] not in {"click", "fill", "submit"} for step in payload["steps"])


def test_uncertainty_fixture_requires_operator_takeover_flag():
    payload = _load("uncertain_submit_recovery.yaml")
    assert payload["uncertainty_trigger"]
    assert payload["requires_operator_takeover_on_uncertainty"] is True


def test_approval_bound_fixtures_require_pre_post_and_trace_artifacts():
    for name in [
        "effectful_billing_address_update.yaml",
        "uncertain_submit_recovery.yaml",
    ]:
        payload = _load(name)
        assert {
            "pre_write_screenshot",
            "post_write_screenshot",
            "dom_snapshot",
            "trace",
        }.issubset(set(payload["expected_artifacts"]))


def test_effectful_fill_steps_declare_values():
    for name in [
        "effectful_billing_address_update.yaml",
        "uncertain_submit_recovery.yaml",
    ]:
        payload = _load(name)
        fill_steps = [step for step in payload["steps"] if step["kind"] == "fill"]
        assert fill_steps
        assert all(step["value"] for step in fill_steps)
