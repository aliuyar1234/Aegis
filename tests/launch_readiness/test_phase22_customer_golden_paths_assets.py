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


def test_phase22_customer_golden_paths_docs_exist():
    assert (ROOT / "docs/design-docs/customer-golden-paths.md").exists()
    assert (ROOT / "docs/runbooks/customer-golden-path-execution.md").exists()


def test_phase22_customer_golden_paths_manifest_validates():
    validate(
        load_yaml("meta/customer-golden-paths.yaml"),
        load_json("schema/jsonschema/customer-golden-paths.schema.json"),
    )


def test_phase22_customer_golden_paths_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-22-customer-golden-paths.yaml")
    assert gate["tests"] == ["TS-059"]
    assert gate["acceptance"] == ["AC-099"]


def test_phase22_customer_golden_paths_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase22_customer_golden_paths.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/customer-golden-path-report.schema.json"))
    assert report["verdict"] == "pass"
