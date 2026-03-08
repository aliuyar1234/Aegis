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


def test_phase24_launch_exception_governance_docs_exist():
    assert (ROOT / "docs/design-docs/launch-exception-governance.md").exists()
    assert (ROOT / "docs/runbooks/launch-exception-response.md").exists()


def test_phase24_launch_exception_governance_manifest_validates():
    validate(
        load_yaml("meta/launch-exception-governance.yaml"),
        load_json("schema/jsonschema/launch-exception-governance.schema.json"),
    )


def test_phase24_launch_exception_governance_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-072")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase24_launch_exception_governance_assets.py -q"
    assert "meta/launch-exception-governance.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-24-launch-exception-governance.yaml")
    assert gate["tests"] == ["TS-072"]
    assert gate["acceptance"] == ["AC-112"]
    assert "meta/launch-exception-governance.yaml" in gate["fixtures"]


def test_phase24_launch_exception_governance_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase24_launch_exception_governance.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/launch-exception-governance-report.schema.json"))
    assert report["verdict"] == "pass"
