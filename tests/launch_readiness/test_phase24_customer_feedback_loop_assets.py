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


def test_phase24_customer_feedback_loop_docs_exist():
    assert (ROOT / "docs/design-docs/customer-feedback-governance.md").exists()
    assert (ROOT / "docs/runbooks/customer-feedback-triage.md").exists()


def test_phase24_customer_feedback_loop_manifest_validates():
    validate(
        load_yaml("meta/customer-feedback-loop.yaml"),
        load_json("schema/jsonschema/customer-feedback-loop.schema.json"),
    )


def test_phase24_customer_feedback_loop_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-071")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase24_customer_feedback_loop_assets.py -q"
    assert "meta/customer-feedback-loop.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-24-customer-feedback-loop.yaml")
    assert gate["tests"] == ["TS-071"]
    assert gate["acceptance"] == ["AC-111"]
    assert "meta/customer-feedback-loop.yaml" in gate["fixtures"]


def test_phase24_customer_feedback_loop_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase24_customer_feedback_loop.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/customer-feedback-loop-report.schema.json"))
    assert report["verdict"] == "pass"
