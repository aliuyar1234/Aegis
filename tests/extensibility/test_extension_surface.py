from pathlib import Path
import json
import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]


def test_extensibility_docs_exist():
    assert (ROOT / 'docs/exec-plans/active/PHASE-10-extensibility-surface.md').exists()
    assert (ROOT / 'docs/design-docs/oss-managed-split.md').exists()


def test_sample_connector_fixture_validates():
    schema = json.loads((ROOT / 'schema/jsonschema/connector-manifest.schema.json').read_text())
    payload = yaml.safe_load((ROOT / 'tests/extensibility/fixtures/sample-connector.yaml').read_text())
    validate(payload, schema)
