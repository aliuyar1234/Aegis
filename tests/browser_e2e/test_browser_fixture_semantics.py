from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    return yaml.safe_load((ROOT / 'tests/browser_e2e/fixtures' / name).read_text())


def test_effectful_fixtures_require_approval_and_policy_defaults():
    for name in ['effectful_billing_address_update.yaml', 'effectful_entitlement_revoke.yaml', 'uncertain_submit_recovery.yaml']:
        payload = _load(name)
        assert payload['requires_approval'] is True
        assert payload['expected_policy_decision'] == 'require_approval'


def test_read_only_fixtures_do_not_require_approval():
    for name in ['read_only_account_lookup.yaml', 'read_only_billing_inspection.yaml']:
        payload = _load(name)
        assert payload['requires_approval'] is False
        assert payload['expected_policy_decision'] == 'allow'
        assert payload['mutation_class'] == 'read_only'
        assert all(step['kind'] not in {'click', 'fill', 'submit'} for step in payload['steps'])


def test_uncertainty_fixture_requires_operator_takeover_flag():
    payload = _load('uncertain_submit_recovery.yaml')
    assert payload['uncertainty_trigger']
    assert payload['requires_operator_takeover_on_uncertainty'] is True


def test_effectful_and_uncertainty_fixtures_require_trace_artifacts():
    for name in [
        'effectful_billing_address_update.yaml',
        'effectful_entitlement_revoke.yaml',
        'uncertain_submit_recovery.yaml',
    ]:
        payload = _load(name)
        assert 'trace' in payload['expected_artifacts']
