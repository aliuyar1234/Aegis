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


def test_phase17_mobility_artifacts_exist_and_validate():
    validate(load_yaml("meta/session-mobility-manifest.yaml"), load_json("schema/jsonschema/session-mobility-manifest.schema.json"))
    assert (ROOT / "docs/design-docs/session-mobility.md").exists()
    assert (ROOT / "scripts/run_phase17_session_mobility.py").exists()


def test_phase17_mobility_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-040")

    assert suite["command"] == "pytest tests/regional_failover/test_phase17_mobility_assets.py -q"
    assert "meta/session-mobility-manifest.yaml" in suite["paths"]
    assert "tests/phase-gates/phase-17-session-mobility.yaml" in suite["paths"]


def test_phase17_mobility_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-17-session-mobility.yaml")

    assert gate["phase"] == "PHASE-17"
    assert gate["tests"] == ["TS-040"]
    assert gate["acceptance"] == ["AC-080"]
    assert "meta/session-mobility-manifest.yaml" in gate["fixtures"]


def test_phase17_mobility_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase17_session_mobility.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/session-mobility-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["scenario_results"]) == 3
