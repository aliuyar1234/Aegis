from pathlib import Path
import json

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / 'tests/media/fixtures'


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text())


def test_media_docs_and_gate_exist():
    assert (ROOT / 'docs/exec-plans/active/PHASE-11-voice-media-path.md').exists()
    assert (ROOT / 'docs/design-docs/media-topology.md').exists()
    assert (ROOT / 'docs/design-docs/future-voice-media.md').exists()
    assert (ROOT / 'docs/design-docs/media-sidecar-contracts.md').exists()
    assert (ROOT / 'docs/design-docs/media-session-extensions.md').exists()
    assert (ROOT / 'docs/design-docs/media-operator-surfaces.md').exists()
    assert (ROOT / 'docs/runbooks/media-qos-degradation.md').exists()
    assert (ROOT / 'docs/runbooks/media-recording-pipeline.md').exists()
    assert (ROOT / 'tests/phase-gates/media-expansion.yaml').exists()


def test_media_contract_fixtures_validate_against_schemas():
    fixture_schema_pairs = [
        ('sample-media-sidecars.yaml', 'media-sidecar-catalog.schema.json'),
        ('sample-media-session-extension.yaml', 'media-session-extension.schema.json'),
        ('sample-operator-media-session-view.yaml', 'operator-media-session-view.schema.json'),
        ('sample-media-topology.yaml', 'media-topology-policy.schema.json'),
    ]

    for fixture_name, schema_name in fixture_schema_pairs:
        payload = load_yaml(FIXTURES / fixture_name)
        schema = json.loads((ROOT / 'schema/jsonschema' / schema_name).read_text())
        validate(payload, schema)


def test_phase11_suite_registry_matches_media_pytest_contract():
    suites = load_yaml(ROOT / 'meta/test-suites.yaml')['test_suites']
    suite = next(item for item in suites if item['id'] == 'TS-015')

    assert suite['command'] == 'pytest tests/media -q'
    assert 'tests/media/fixtures' in suite['paths']
    assert 'docs/design-docs/media-sidecar-contracts.md' in suite['paths']
    assert 'docs/runbooks/media-qos-degradation.md' in suite['paths']


def test_media_phase_gate_references_concrete_contracts_and_runbooks():
    gate = load_yaml(ROOT / 'tests/phase-gates/media-expansion.yaml')
    fixtures = set(gate['fixtures'])

    assert gate['tests'] == ['TS-015']
    assert {'AC-045', 'AC-046', 'AC-047', 'AC-048'} == set(gate['acceptance'])
    assert 'schema/jsonschema/media-sidecar-catalog.schema.json' in fixtures
    assert 'schema/jsonschema/media-session-extension.schema.json' in fixtures
    assert 'schema/jsonschema/operator-media-session-view.schema.json' in fixtures
    assert 'tests/media/fixtures/sample-media-topology.yaml' in fixtures
    assert 'docs/runbooks/media-qos-degradation.md' in fixtures
    assert 'docs/runbooks/media-recording-pipeline.md' in fixtures

    step_ids = {step['id'] for step in gate['steps']}
    assert {'media-boundaries', 'session-extension', 'degraded-qos'} <= step_ids


def test_media_docs_make_boundaries_explicit():
    sidecars = (ROOT / 'docs/design-docs/media-sidecar-contracts.md').read_text().lower()
    session_extensions = (ROOT / 'docs/design-docs/media-session-extensions.md').read_text().lower()
    operator_surfaces = (ROOT / 'docs/design-docs/media-operator-surfaces.md').read_text().lower()
    future = (ROOT / 'docs/design-docs/future-voice-media.md').read_text().lower()
    topology = (ROOT / 'docs/design-docs/media-topology.md').read_text().lower()

    assert 'elixir remains the session owner' in sidecars
    assert 'replay does not consume raw packets as truth' in sidecars
    assert 'raw packet buffers' in session_extensions
    assert 'operator handoff requirement must be explicit' in session_extensions
    assert 'qos state and degradation reason' in operator_surfaces
    assert 'replay must not pretend to be a raw packet scrubber' in operator_surfaces
    assert 'capacity isolation remains compatible' in future
    assert 'admission and recording responses must be explicit' in topology


def test_media_runbooks_and_failure_catalog_are_wired():
    failure_catalog = load_yaml(ROOT / 'meta/failure-runbooks.yaml')['failures']
    ids = {item['id']: item for item in failure_catalog}

    assert ids['media_qos_degradation']['runbook'] == 'docs/runbooks/media-qos-degradation.md'
    assert ids['media_recording_pipeline']['runbook'] == 'docs/runbooks/media-recording-pipeline.md'
    assert ids['media_qos_degradation']['operator_surface'] == 'session-detail'
    assert ids['media_recording_pipeline']['operator_surface'] == 'session-detail'

    qos_runbook = (ROOT / 'docs/runbooks/media-qos-degradation.md').read_text().lower()
    recording_runbook = (ROOT / 'docs/runbooks/media-recording-pipeline.md').read_text().lower()

    assert 'operator handoff' in qos_runbook
    assert 'recording status becomes explicit' in recording_runbook


def test_media_fixtures_capture_capacity_and_handoff_rules():
    session_extension = load_yaml(FIXTURES / 'sample-media-session-extension.yaml')
    operator_view = load_yaml(FIXTURES / 'sample-operator-media-session-view.yaml')
    topology = load_yaml(FIXTURES / 'sample-media-topology.yaml')

    assert session_extension['capacity_isolation']['pool_class'] == 'tenant_isolated_media_pool'
    assert session_extension['handoff']['operator_handoff_required'] is True
    assert operator_view['handoff_required'] is True
    assert 'docs/runbooks/media-qos-degradation.md' in operator_view['recommended_runbooks']
    assert topology['degradation_policies']['admission_response'] == 'require_operator_handoff'
    assert (ROOT / topology['handoff_rules']['runbook_ref']).exists()
    for runbook in operator_view['recommended_runbooks']:
        assert (ROOT / runbook).exists()
