from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_recovery_runbooks_exist():
    for name in ['worker-crash.md','node-loss.md','lease-ambiguity.md','event-corruption-quarantine.md','duplicate-execution.md']:
        assert (ROOT / 'docs/runbooks' / name).exists()


def test_node_loss_runbook_mentions_phase_3_signals():
    content = (ROOT / 'docs/runbooks' / 'node-loss.md').read_text(encoding='utf-8')
    assert 'system.lease_lost' in content
    assert 'system.node_recovered' in content
    assert 'lease epoch' in content


def test_lease_ambiguity_runbook_mentions_fencing_and_degraded_mode():
    content = (ROOT / 'docs/runbooks' / 'lease-ambiguity.md').read_text(encoding='utf-8')
    assert 'health.degraded' in content
    assert 'fenced/degraded' in content
    assert 'one node owns the next epoch' in content


def test_duplicate_execution_runbook_mentions_uncertainty_and_replay_markers():
    content = (ROOT / 'docs/runbooks' / 'duplicate-execution.md').read_text(encoding='utf-8')
    assert 'duplicate completion/failure observed for same execution/action' in content
    assert 'surface uncertainty' in content
    assert 'duplicate markers in replay' in content
