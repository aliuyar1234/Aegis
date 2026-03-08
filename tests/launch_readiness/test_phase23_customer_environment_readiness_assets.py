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


def test_phase23_customer_environment_docs_exist():
    assert (ROOT / "docs/design-docs/customer-environment-readiness.md").exists()
    assert (ROOT / "docs/operations/customer-environment-readiness.md").exists()
    assert (ROOT / "docs/runbooks/customer-environment-acceptance.md").exists()


def test_phase23_customer_environment_manifest_validates():
    validate(
        load_yaml("meta/customer-environment-readiness.yaml"),
        load_json("schema/jsonschema/customer-environment-readiness.schema.json"),
    )


def test_phase23_customer_environment_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-066")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase23_customer_environment_readiness_assets.py -q"
    assert "meta/customer-environment-readiness.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-23-customer-environment-readiness.yaml")
    assert gate["tests"] == ["TS-066"]
    assert gate["acceptance"] == ["AC-106"]
    assert "meta/customer-environment-readiness.yaml" in gate["fixtures"]


def test_phase23_customer_environment_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase23_customer_environment_readiness.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/customer-environment-readiness-report.schema.json"))
    assert report["verdict"] == "pass"
