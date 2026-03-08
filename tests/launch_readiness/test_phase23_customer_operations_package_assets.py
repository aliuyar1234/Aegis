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


def test_phase23_customer_operations_docs_exist():
    assert (ROOT / "docs/design-docs/customer-operations-package.md").exists()
    assert (ROOT / "docs/operations/customer-operations.md").exists()
    assert (ROOT / "docs/runbooks/customer-operations-handshake.md").exists()


def test_phase23_customer_operations_manifest_validates():
    validate(
        load_yaml("meta/customer-operations-package.yaml"),
        load_json("schema/jsonschema/customer-operations-package.schema.json"),
    )


def test_phase23_customer_operations_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-067")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase23_customer_operations_package_assets.py -q"
    assert "meta/customer-operations-package.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-23-customer-operations-docs.yaml")
    assert gate["tests"] == ["TS-067"]
    assert gate["acceptance"] == ["AC-107"]
    assert "meta/customer-operations-package.yaml" in gate["fixtures"]


def test_phase23_customer_operations_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase23_customer_operations_package.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/customer-operations-package-report.schema.json"))
    assert report["verdict"] == "pass"
