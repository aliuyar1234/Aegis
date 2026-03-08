from pathlib import Path
import json
import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'schema/jsonschema/connector-manifest.schema.json').read_text())
POLICY_SCHEMA = json.loads(
    (ROOT / 'schema/jsonschema/extension-compatibility-policy.schema.json').read_text()
)
PACK_SCHEMA = json.loads((ROOT / 'schema/jsonschema/extension-pack-manifest.schema.json').read_text())
POLICY = yaml.safe_load((ROOT / 'meta/extension-compatibility-policy.yaml').read_text())
PACK_ROOT = ROOT / 'tests/extensibility/fixtures/sample-extension-pack'
PACK = yaml.safe_load((PACK_ROOT / 'pack.yaml').read_text())


def load_fixture(name: str):
    return yaml.safe_load((ROOT / 'tests/extensibility' / 'fixtures' / name).read_text())


def resolve_from(base: Path, relative_path: str) -> Path:
    return (base / relative_path).resolve()


def version_matches(version: str, expected: str) -> bool:
    if expected.endswith('.x'):
        return version.startswith(expected[:-1])
    return version == expected


def version_in_range(version: str, version_range: dict) -> bool:
    return version_matches(version, version_range['min']) and version_matches(version, version_range['max'])


def test_extensibility_docs_exist():
    assert (ROOT / 'docs/exec-plans/active/PHASE-10-extensibility-surface.md').exists()
    assert (ROOT / 'docs/design-docs/extensibility-surface.md').exists()
    assert (ROOT / 'docs/design-docs/mcp-adapter-boundary.md').exists()
    assert (ROOT / 'docs/design-docs/extension-compatibility-policy.md').exists()
    assert (ROOT / 'docs/design-docs/extension-review-rubric.md').exists()


def test_extension_compatibility_policy_validates():
    validate(POLICY, POLICY_SCHEMA)


def test_sample_connector_fixture_validates():
    validate(load_fixture('sample-connector.yaml'), SCHEMA)


def test_sample_artifact_processor_fixture_validates():
    validate(load_fixture('sample-artifact-processor.yaml'), SCHEMA)


def test_sample_mcp_adapter_fixture_validates():
    validate(load_fixture('sample-mcp-adapter.yaml'), SCHEMA)


def test_sample_extension_pack_validates():
    validate(PACK, PACK_SCHEMA)


def test_extension_fixtures_define_common_contract_boundaries():
    connector = load_fixture('sample-connector.yaml')
    processor = load_fixture('sample-artifact-processor.yaml')
    mcp_adapter = load_fixture('sample-mcp-adapter.yaml')

    for payload in (connector, processor, mcp_adapter):
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
    assert mcp_adapter['mcp_adapter']['protocol_role'] == 'external_tool_adapter'
    assert mcp_adapter['mcp_adapter']['session_binding']['maps_to_action_requests_only'] is True
    assert mcp_adapter['mcp_adapter']['protocol_boundary']['mcp_is_internal_runtime_protocol'] is False
    assert mcp_adapter['mcp_adapter']['protocol_boundary']['writes_canonical_state_directly'] is False


def test_sample_manifests_comply_with_extension_compatibility_policy():
    policy_rules = POLICY['compatibility_rules']
    current_runtime = POLICY['aegis_runtime']['current_release']
    current_extension_api = POLICY['extension_api']['current_version']
    current_tool_registry = POLICY['tool_registry']['current_version']

    for name in (
        'sample-connector.yaml',
        'sample-artifact-processor.yaml',
        'sample-mcp-adapter.yaml',
    ):
        payload = load_fixture(name)

        assert payload['runtime_contract_version'] in POLICY['aegis_runtime']['supported_contract_versions']
        assert payload['extension_api_version'] in POLICY['extension_api']['supported_versions']
        assert payload['sdk']['language'] in POLICY['supported_sdk_languages']
        assert set(payload['compatibility']['supported_tiers']) <= set(POLICY['supported_tiers'])

        if policy_rules['require_bounded_runtime_range']:
            assert version_in_range(current_runtime, payload['compatibility']['aegis_runtime'])
        if policy_rules['require_bounded_extension_api_range']:
            assert version_in_range(current_extension_api, payload['compatibility']['extension_api'])
        if policy_rules['require_bounded_tool_registry_range']:
            assert version_in_range(current_tool_registry, payload['compatibility']['tool_registry'])
        if policy_rules['forbid_open_ended_ranges']:
            for range_key in ('aegis_runtime', 'extension_api', 'tool_registry'):
                assert payload['compatibility'][range_key]['min'] != '*'
                assert payload['compatibility'][range_key]['max'] != '*'

    assert policy_rules['mcp_adapters_external_only'] is True


def test_sample_extension_pack_layout_and_member_manifests_are_reviewable():
    readme_path = resolve_from(PACK_ROOT, PACK['readme_ref'])
    policy_path = resolve_from(PACK_ROOT, PACK['compatibility_policy_ref'])
    rubric_path = resolve_from(PACK_ROOT, PACK['review_rubric_ref'])

    assert readme_path.exists()
    assert policy_path == (ROOT / 'meta/extension-compatibility-policy.yaml').resolve()
    assert rubric_path == (ROOT / 'docs/design-docs/extension-review-rubric.md').resolve()

    for directory_key in ('connectors_dir', 'artifact_processors_dir', 'mcp_adapters_dir'):
        assert resolve_from(PACK_ROOT, PACK['layout'][directory_key]).is_dir()

    member_kinds = set()
    for member in PACK['members']:
        member_path = resolve_from(PACK_ROOT, member['manifest_ref'])
        assert member_path.exists()
        payload = yaml.safe_load(member_path.read_text())
        validate(payload, SCHEMA)
        assert payload['id'] == member['id']
        assert payload['kind'] == member['kind']
        member_kinds.add(member['kind'])

    assert member_kinds == {'tool_connector', 'artifact_processor', 'mcp_adapter'}


def test_review_rubric_mentions_required_phase10_gates():
    rubric = (ROOT / 'docs/design-docs/extension-review-rubric.md').read_text().lower()

    assert 'compatibility ranges are bounded' in rubric
    assert 'direct canonical writes' in rubric
    assert 'outbox bypass' in rubric
    assert 'mcp adapters stay external-tool adapters only' in rubric
    assert 'sample extension pack layout exists' in rubric
