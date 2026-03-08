from pathlib import Path
import re
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


def test_phase09_storage_migrations_pin_universal_scope_columns():
    core_sql = (ROOT / 'apps/aegis_events/priv/postgres/migrations/202603080001_phase_02_core.sql').read_text()
    bridge_sql = (ROOT / 'apps/aegis_events/priv/postgres/migrations/202603080002_phase_04_execution_bridge.sql').read_text()

    checkpoints_block = re.search(r'CREATE TABLE IF NOT EXISTS session_checkpoints \((.*?)\);', core_sql, re.S)
    outbox_block = re.search(r'CREATE TABLE IF NOT EXISTS outbox \((.*?)\);', core_sql, re.S)
    sessions_block = re.search(r'CREATE TABLE IF NOT EXISTS sessions \((.*?)\);', core_sql, re.S)
    executions_block = re.search(r'CREATE TABLE IF NOT EXISTS action_executions \((.*?)\);', bridge_sql, re.S)

    assert sessions_block
    assert checkpoints_block
    assert outbox_block
    assert executions_block

    assert 'isolation_tier TEXT NOT NULL' in sessions_block.group(1)

    for block in (checkpoints_block.group(1), outbox_block.group(1), executions_block.group(1)):
        assert 'tenant_id TEXT NOT NULL' in block
        assert 'workspace_id TEXT NOT NULL' in block

    assert 'CREATE INDEX IF NOT EXISTS session_checkpoints_scope_seq_idx' in core_sql
    assert 'CREATE INDEX IF NOT EXISTS outbox_scope_pending_idx' in core_sql
    assert 'CREATE INDEX IF NOT EXISTS action_executions_scope_status_idx' in bridge_sql


def test_security_suite_command_covers_runtime_scope_enforcement():
    data = yaml.safe_load((ROOT / 'meta/test-suites.yaml').read_text())
    suite = next(item for item in data['test_suites'] if item['id'] == 'TS-011')

    assert suite['command'] == 'python3 scripts/run_security_suite.py'
    assert 'apps/aegis_policy/test/authorizer_test.exs' in suite['paths']
    assert 'apps/aegis_events/test/replay/replay_test.exs' in suite['paths']
    assert 'apps/aegis_execution_bridge/test/execution_bridge/execution_bridge_test.exs' in suite['paths']
    assert 'apps/aegis_execution_bridge/test/execution_bridge/admission_control_test.exs' in suite['paths']
    assert 'apps/aegis_gateway/test/operator_console/operator_console_authorization_test.exs' in suite['paths']
    assert 'docs/design-docs/security-governance.md' in suite['paths']
    assert 'docs/threat-models/runtime-threat-model.md' in suite['paths']
    assert 'docs/threat-models/browser-wedge-threats.md' in suite['paths']
    assert 'docs/threat-models/enterprise-control-matrix.md' in suite['paths']


def test_phase09_security_docs_capture_audit_and_isolation_controls():
    governance = (ROOT / 'docs/design-docs/security-governance.md').read_text().lower()
    runtime = (ROOT / 'docs/threat-models/runtime-threat-model.md').read_text().lower()
    browser = (ROOT / 'docs/threat-models/browser-wedge-threats.md').read_text().lower()
    enterprise = (ROOT / 'docs/threat-models/enterprise-control-matrix.md').read_text().lower()
    threat_index = (ROOT / 'docs/threat-models/README.md').read_text().lower()

    assert 'rbac/abac' in governance
    assert 'concurrent browser contexts' in governance
    assert 'concurrent effectful actions' in governance
    assert 'worker_pool_id' in governance
    assert 'dispatch_route_key' in governance
    assert 'retention_class' in governance
    assert 'redaction_state' in governance

    assert 'quota and admission control' in runtime
    assert 'worker_pool_id' in runtime
    assert 'redaction metadata' in runtime

    assert 'routed subjects' in browser
    assert 'before/after screenshots' in browser
    assert 'capability tokens' in browser
    assert 'uncertain side effects' in browser

    assert 'quota and admission control' in enterprise
    assert 'tiered isolation routing' in enterprise
    assert 'audit, evidence, and replay' in enterprise
    assert 'runbooks and operator recovery' in enterprise
    assert 'enterprise-control-matrix.md' in threat_index
