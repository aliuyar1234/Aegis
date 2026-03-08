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


def test_phase25_ga_transition_artifacts_exist_and_validate():
    validate(
        load_yaml("meta/ga-transition-gate-manifest.yaml"),
        load_json("schema/jsonschema/ga-transition-gate-manifest.schema.json"),
    )
    validate(
        load_yaml("meta/phase25-ga-transition-evidence-manifest.yaml"),
        load_json("schema/jsonschema/phase25-ga-transition-evidence-manifest.schema.json"),
    )
    assert (ROOT / "schema/jsonschema/ga-transition-gate-report.schema.json").exists()
    assert (ROOT / "schema/jsonschema/phase25-ga-transition-evidence-bundle.schema.json").exists()
    assert (ROOT / "docs/generated/phase-25-ga-transition-evidence.json").exists()


def test_phase25_ga_transition_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-078")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase25_ga_transition_gate_plan_assets.py -q"
    assert "meta/ga-transition-gate-manifest.yaml" in suite["paths"]
    assert "docs/generated/phase-25-ga-transition-evidence.json" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-25-ga-transition-gate.yaml")
    assert gate["tests"] == ["TS-078"]
    assert gate["acceptance"] == ["AC-118"]
    assert "meta/ga-transition-gate-manifest.yaml" in gate["fixtures"]
    assert "docs/generated/phase-25-ga-transition-evidence.json" in gate["fixtures"]


def test_phase25_ga_transition_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase25_ga_transition_gate.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/ga-transition-gate-report.schema.json"))
    assert report["verdict"] == "pass"


def test_phase25_evidence_builder_reproduces_committed_bundle():
    completed = subprocess.run(
        [sys.executable, "scripts/build_phase25_ga_transition_evidence.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    bundle = json.loads(completed.stdout)
    validate(bundle, load_json("schema/jsonschema/phase25-ga-transition-evidence-bundle.schema.json"))
    committed = load_json("docs/generated/phase-25-ga-transition-evidence.json")
    assert bundle == committed
    assert bundle["verdict"] == "pass"
    assert len(bundle["reports"]) == 5
