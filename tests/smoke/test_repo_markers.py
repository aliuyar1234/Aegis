from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_core_markers_exist():
    for path in ['PATCHLOG_V2.md', 'PATCHLOG_V3.md', 'AUDIT_REMEDIATION_MATRIX.md', 'meta/current-phase.yaml']:
        assert (ROOT / path).exists()
