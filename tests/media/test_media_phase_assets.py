from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_media_docs_and_gate_exist():
    assert (ROOT / 'docs/exec-plans/active/PHASE-11-voice-media-path.md').exists()
    assert (ROOT / 'docs/design-docs/media-topology.md').exists()
    assert (ROOT / 'tests/phase-gates/media-expansion.yaml').exists()
