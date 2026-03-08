from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def test_phase26_field_evidence_corpus_is_committed_in_ssot():
    assert (ROOT / "docs/exec-plans/active/PHASE-26-live-customer-operations-and-release-automation.md").exists()
    gate = load_yaml("tests/phase-gates/phase-26-field-evidence-corpus.yaml")
    assert gate["tests"] == ["TS-081"]
    assert gate["acceptance"] == ["AC-121"]
    tasks = load_yaml("work-items/task-index.yaml")["tasks"]
    task = next(item for item in tasks if item["id"] == "P26-T03")
    assert task["phase"] == "PHASE-26"
    assert task["status"] == "planned"
