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


def test_phase23_real_infrastructure_docs_exist():
    assert (ROOT / "docs/design-docs/real-infrastructure-proving.md").exists()
    assert (ROOT / "docs/runbooks/production-like-proving.md").exists()


def test_phase23_real_infrastructure_manifest_validates():
    validate(
        load_yaml("meta/real-infrastructure-proving.yaml"),
        load_json("schema/jsonschema/real-infrastructure-proving.schema.json"),
    )


def test_phase23_real_infrastructure_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-064")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase23_real_infrastructure_proving_assets.py -q"
    assert "meta/real-infrastructure-proving.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-23-real-infrastructure-proving.yaml")
    assert gate["tests"] == ["TS-064"]
    assert gate["acceptance"] == ["AC-104"]
    assert "meta/real-infrastructure-proving.yaml" in gate["fixtures"]


def test_phase23_real_infrastructure_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase23_real_infrastructure_proving.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/real-infrastructure-proving-report.schema.json"))
    assert report["verdict"] == "pass"
