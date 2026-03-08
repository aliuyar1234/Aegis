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


def test_phase16_placement_artifacts_exist_and_validate():
    validate(load_yaml("meta/placement-policies.yaml"), load_json("schema/jsonschema/placement-policies.schema.json"))
    assert (ROOT / "docs/design-docs/placement-engine.md").exists()
    assert (ROOT / "scripts/run_phase16_placement.py").exists()
    assert (ROOT / "schema/jsonschema/placement-decision.schema.json").exists()
    assert (ROOT / "schema/jsonschema/placement-report.schema.json").exists()


def test_phase16_placement_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-032")

    assert suite["command"] == "pytest tests/placement -q"
    assert "meta/placement-policies.yaml" in suite["paths"]
    assert "scripts/run_phase16_placement.py" in suite["paths"]
    assert "tests/phase-gates/phase-16-placement.yaml" in suite["paths"]


def test_phase16_placement_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-16-placement.yaml")

    assert gate["phase"] == "PHASE-16"
    assert gate["tests"] == ["TS-032"]
    assert gate["acceptance"] == ["AC-072"]
    assert "meta/placement-policies.yaml" in gate["fixtures"]


def test_phase16_placement_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase16_placement.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/placement-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["decisions"]) == 4
