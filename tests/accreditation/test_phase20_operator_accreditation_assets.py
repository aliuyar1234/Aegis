from pathlib import Path
import json
import subprocess
import sys

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_phase20_operator_accreditation_docs_exist():
    assert (ROOT / "docs/exec-plans/active/PHASE-20-operational-lifecycle-governance.md").exists()
    assert (ROOT / "docs/design-docs/operator-accreditation.md").exists()
    assert (ROOT / "docs/runbooks/operator-accreditation-renewal.md").exists()


def test_phase20_operator_accreditation_manifest_validates():
    validate(
        load_yaml("meta/operator-accreditation.yaml"),
        load_json("schema/jsonschema/operator-accreditation.schema.json"),
    )


def test_phase20_operator_accreditation_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-052")

    assert suite["command"] == "pytest tests/accreditation -q"
    assert "meta/operator-accreditation.yaml" in suite["paths"]
    assert "scripts/run_phase20_operator_accreditation.py" in suite["paths"]


def test_phase20_operator_accreditation_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-20-operator-accreditation.yaml")

    assert gate["phase"] == "PHASE-20"
    assert gate["tests"] == ["TS-052"]
    assert gate["acceptance"] == ["AC-092"]
    assert "meta/operator-accreditation.yaml" in gate["fixtures"]
    assert "scripts/run_phase20_operator_accreditation.py" in gate["fixtures"]


def test_phase20_operator_accreditation_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase20_operator_accreditation.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/operator-accreditation-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["tracks"]) == 2
    assert all(item["deployment_track_count"] >= 1 for item in report["tracks"])
