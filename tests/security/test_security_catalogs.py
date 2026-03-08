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
