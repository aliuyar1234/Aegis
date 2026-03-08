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


def test_phase21_evaluation_deployment_docs_exist():
    assert (ROOT / "docs/operations/evaluation-deployment.md").exists()
    assert (ROOT / "infra/local/README.md").exists()


def test_phase21_evaluation_deployment_manifest_validates():
    validate(
        load_yaml("meta/evaluation-deployment-profile.yaml"),
        load_json("schema/jsonschema/evaluation-deployment-profile.schema.json"),
    )


def test_phase21_evaluation_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-058")

    assert suite["command"] == "pytest tests/launch_readiness/test_phase21_evaluation_deployment_assets.py -q"
    assert "meta/evaluation-deployment-profile.yaml" in suite["paths"]
    assert "scripts/run_phase21_evaluation_deployment.py" in suite["paths"]


def test_phase21_evaluation_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-21-evaluation-deployment.yaml")

    assert gate["phase"] == "PHASE-21"
    assert gate["tests"] == ["TS-058"]
    assert gate["acceptance"] == ["AC-098"]
    assert "meta/evaluation-deployment-profile.yaml" in gate["fixtures"]
    assert "scripts/run_phase21_evaluation_deployment.py" in gate["fixtures"]


def test_phase21_evaluation_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase21_evaluation_deployment.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/evaluation-deployment-report.schema.json"))
    assert report["verdict"] == "pass"
    assert any(item["name"] == "postgres" for item in report["services"])
