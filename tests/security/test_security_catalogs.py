from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_rbac_and_abac_catalogs_exist():
    assert (ROOT / 'meta/rbac-roles.yaml').exists()
    assert (ROOT / 'meta/abac-attributes.yaml').exists()


def test_failure_runbook_mapping_exists():
    data = yaml.safe_load((ROOT / 'meta/failure-runbooks.yaml').read_text())
    assert any(item['id'] == 'worker_crash' for item in data['failures'])


def test_worker_db_guardrails_cover_canonical_tables():
    data = yaml.safe_load((ROOT / 'meta/worker-db-guardrails.yaml').read_text())
    allowed = set(data['worker_db_guardrails']['allowed_tables'])
    forbidden = set(data['worker_db_guardrails']['forbidden_tables'])

    assert allowed == {'action_executions', 'worker_registrations'}
    assert {'sessions', 'session_events', 'session_checkpoints', 'session_leases', 'approvals', 'outbox'} <= forbidden


def test_capability_token_claims_enforce_scoped_identity_fields():
    schema = yaml.safe_load((ROOT / 'schema/jsonschema/capability-token-claims.schema.json').read_text())
    required = set(schema['required'])

    assert {
        'tenant_id',
        'workspace_id',
        'session_id',
        'action_id',
        'tool_id',
        'approved_argument_digest',
        'dangerous_action_class',
        'expires_at',
        'lease_epoch',
        'side_effect_class',
        'scopes',
        'issued_to_worker_kind',
    } <= required


def test_approval_request_schema_binds_exact_action_scope():
    schema = yaml.safe_load((ROOT / 'schema/jsonschema/approval-request.schema.json').read_text())
    required = set(schema['required'])

    assert {
        'approval_id',
        'tenant_id',
        'workspace_id',
        'session_id',
        'action_id',
        'action_hash',
        'risk_class',
        'dangerous_action_class',
        'expires_at',
        'lease_epoch',
    } <= required
