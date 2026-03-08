from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_phase_gate_assets_exist():
    assert (ROOT / 'tests/phase-gates/internal-demo.yaml').exists()
    assert (ROOT / 'tests/phase-gates/public-demo.yaml').exists()


def test_failure_runbook_catalog_maps_phase_3_recovery_failures():
    content = (ROOT / 'meta/failure-runbooks.yaml').read_text(encoding='utf-8')
    assert 'id: node_loss' in content
    assert 'id: lease_ambiguity' in content
    assert 'runbook: docs/runbooks/node-loss.md' in content
    assert 'runbook: docs/runbooks/lease-ambiguity.md' in content
    assert 'system.node_recovered' in content
    assert 'health.degraded' in content
