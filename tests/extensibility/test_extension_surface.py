from pathlib import Path
import json
import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'schema/jsonschema/connector-manifest.schema.json').read_text())


def load_fixture(name: str):
    return yaml.safe_load((ROOT / 'tests/extensibility' / 'fixtures' / name).read_text())


def test_extensibility_docs_exist():
    assert (ROOT / 'docs/exec-plans/active/PHASE-10-extensibility-surface.md').exists()
    assert (ROOT / 'docs/design-docs/extensibility-surface.md').exists()


def test_sample_connector_fixture_validates():
    validate(load_fixture('sample-connector.yaml'), SCHEMA)


def test_sample_artifact_processor_fixture_validates():
    validate(load_fixture('sample-artifact-processor.yaml'), SCHEMA)


def test_extension_fixtures_define_common_contract_boundaries():
    connector = load_fixture('sample-connector.yaml')
    processor = load_fixture('sample-artifact-processor.yaml')

    for payload in (connector, processor):
        assert set(payload['lifecycle']) == {'install', 'start', 'health_check', 'run', 'shutdown'}
        assert set(payload['compatibility']) == {
            'aegis_runtime',
            'extension_api',
            'tool_registry',
            'supported_tiers',
        }
        assert set(payload['capability_boundary']) == {
            'required_scopes',
            'allowed_tools',
            'dangerous_action_classes',
            'secrets',
            'network',
            'artifact_access',
        }

    assert connector['tool_connector']['tools'][0]['tool_id'] == 'billing.lookup'
    assert processor['artifact_processor']['processing_mode'] == 'batch'
    assert processor['artifact_processor']['max_input_bytes'] > 0
