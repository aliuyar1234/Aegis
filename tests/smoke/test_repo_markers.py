from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_core_markers_exist():
    for path in ['docs/project/patchlog-v2.md', 'docs/project/patchlog-v3.md', 'docs/project/audit-remediation-matrix.md', 'meta/current-phase.yaml']:
        assert (ROOT / path).exists()
