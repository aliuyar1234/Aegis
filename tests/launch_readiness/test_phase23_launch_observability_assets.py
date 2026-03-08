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


def test_phase23_launch_observability_docs_exist():
    assert (ROOT / "docs/design-docs/launch-observability-baseline.md").exists()
    assert (ROOT / "docs/operations/launch-observability.md").exists()
    assert (ROOT / "docs/runbooks/launch-observability-review.md").exists()


def test_phase23_launch_observability_manifest_validates():
    validate(
        load_yaml("meta/launch-observability-baseline.yaml"),
        load_json("schema/jsonschema/launch-observability-baseline.schema.json"),
    )


def test_phase23_launch_observability_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-065")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase23_launch_observability_assets.py -q"
    assert "meta/launch-observability-baseline.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-23-launch-observability.yaml")
    assert gate["tests"] == ["TS-065"]
    assert gate["acceptance"] == ["AC-105"]
    assert "meta/launch-observability-baseline.yaml" in gate["fixtures"]


def test_phase23_launch_observability_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase23_launch_observability.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/launch-observability-report.schema.json"))
    assert report["verdict"] == "pass"
