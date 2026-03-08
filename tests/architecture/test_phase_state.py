from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_current_phase_is_phase_01():
    data = yaml.safe_load((ROOT / 'meta/current-phase.yaml').read_text())
    assert data['current_phase'] == 'PHASE-01'
