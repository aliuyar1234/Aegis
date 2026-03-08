from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_dangerous_action_catalog_exists_and_has_browser_classes():
    data = yaml.safe_load((ROOT / 'meta/dangerous-action-classes.yaml').read_text())
    ids = {item['id'] for item in data['dangerous_action_classes']}
    decisions = {item['id']: item['default_decision'] for item in data['dangerous_action_classes']}
    assert 'browser_write_medium' in ids
    assert 'browser_write_high' in ids
    assert decisions['browser_write_low'] == 'allow_with_constraints'
    assert decisions['browser_write_medium'] == 'require_approval'
    assert decisions['browser_write_high'] == 'deny_without_explicit_policy'


def test_capability_token_schema_exists():
    assert (ROOT / 'schema/jsonschema/capability-token-claims.schema.json').exists()


def test_mutating_browser_tools_require_dangerous_action_classes():
    registry = yaml.safe_load((ROOT / 'schema/tool-registry.yaml').read_text())
    mutating = {
        descriptor['tool_id']: descriptor
        for descriptor in registry['tools']
        if descriptor['risk_class'] == 'browser_write'
    }

    assert mutating['browser.click']['dangerous_action_class'] == 'browser_write_low'
    assert mutating['browser.submit']['dangerous_action_class'] == 'browser_write_medium'
    assert mutating['browser.delete']['dangerous_action_class'] == 'browser_write_high'
