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


def test_phase17_evacuation_artifacts_exist_and_validate():
    validate(load_yaml("meta/regional-evacuation-fixtures.yaml"), load_json("schema/jsonschema/regional-evacuation-manifest.schema.json"))
    assert (ROOT / "docs/design-docs/regional-evacuation.md").exists()
    assert (ROOT / "docs/runbooks/regional-evacuation.md").exists()
    assert (ROOT / "docs/runbooks/regional-promotion.md").exists()
    assert (ROOT / "scripts/run_phase17_regional_evacuation.py").exists()


def test_phase17_evacuation_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-039")

    assert suite["command"] == "pytest tests/regional_failover/test_phase17_evacuation_assets.py -q"
    assert "meta/regional-evacuation-fixtures.yaml" in suite["paths"]
    assert "docs/runbooks/regional-evacuation.md" in suite["paths"]


def test_phase17_evacuation_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-17-regional-evacuation.yaml")

    assert gate["phase"] == "PHASE-17"
    assert gate["tests"] == ["TS-039"]
    assert gate["acceptance"] == ["AC-079"]
    assert "meta/regional-evacuation-fixtures.yaml" in gate["fixtures"]


def test_phase17_evacuation_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase17_regional_evacuation.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/regional-evacuation-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["drill_results"]) == 2
