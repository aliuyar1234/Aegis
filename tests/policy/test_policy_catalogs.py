from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_dangerous_action_catalog_exists_and_has_browser_classes():
    data = yaml.safe_load((ROOT / 'meta/dangerous-action-classes.yaml').read_text())
    ids = {item['id'] for item in data['dangerous_action_classes']}
    assert 'browser_write_medium' in ids
    assert 'browser_write_high' in ids


def test_capability_token_schema_exists():
    assert (ROOT / 'schema/jsonschema/capability-token-claims.schema.json').exists()
