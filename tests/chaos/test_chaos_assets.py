from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_phase_gate_assets_exist():
    assert (ROOT / 'tests/phase-gates/internal-demo.yaml').exists()
    assert (ROOT / 'tests/phase-gates/public-demo.yaml').exists()
    assert (ROOT / 'docs/demo-scripts/internal-runtime-credibility.md').exists()
    assert (ROOT / 'docs/demo-scripts/public-mission-control.md').exists()


def test_failure_runbook_catalog_maps_phase_3_recovery_failures():
    content = (ROOT / 'meta/failure-runbooks.yaml').read_text(encoding='utf-8')
    assert 'id: node_loss' in content
    assert 'id: lease_ambiguity' in content
    assert 'runbook: docs/runbooks/node-loss.md' in content
    assert 'runbook: docs/runbooks/lease-ambiguity.md' in content
    assert 'system.node_recovered' in content
    assert 'health.degraded' in content


def test_failure_runbook_catalog_maps_duplicate_execution_to_replay_triage():
    content = (ROOT / 'meta/failure-runbooks.yaml').read_text(encoding='utf-8')
    assert 'id: duplicate_execution' in content
    assert 'runbook: docs/runbooks/duplicate-execution.md' in content
    assert 'operator_surface: replay' in content
    assert 'action.succeeded' in content
    assert 'action.failed' in content


def test_phase_8_demo_gates_require_visible_duplicate_or_uncertain_failures():
    internal_demo = (ROOT / 'tests/phase-gates' / 'internal-demo.yaml').read_text(encoding='utf-8')
    public_demo = (ROOT / 'tests/phase-gates' / 'public-demo.yaml').read_text(encoding='utf-8')

    assert 'AC-034' in internal_demo
    assert 'duplicate side effects are not hidden' in internal_demo
    assert 'no silent duplicate write' in public_demo
    assert 'uncertainty is surfaced if write certainty is unclear' in public_demo


def test_demo_scripts_cover_approval_uncertainty_and_denied_writes():
    public_demo = (ROOT / 'docs/demo-scripts' / 'public-mission-control.md').read_text(encoding='utf-8')
    internal_demo = (ROOT / 'docs/demo-scripts' / 'internal-runtime-credibility.md').read_text(encoding='utf-8')

    assert 'capability-token-gated mutation path' in public_demo
    assert 'denied destructive action evidence' in public_demo
    assert 'duplicate or uncertain write evidence in replay' in internal_demo
