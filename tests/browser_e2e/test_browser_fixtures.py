import json
from pathlib import Path
import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'schema/jsonschema/browser-workflow-fixture.schema.json').read_text())


def test_browser_fixtures_validate():
    for fixture in (ROOT / 'tests/browser_e2e/fixtures').glob('*.yaml'):
        payload = yaml.safe_load(fixture.read_text())
        validate(payload, SCHEMA)
