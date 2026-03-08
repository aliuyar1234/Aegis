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


def test_phase25_service_scale_docs_exist():
    assert (ROOT / "docs/design-docs/service-scale-operations-readiness.md").exists()
    assert (ROOT / "docs/operations/service-scale-operations.md").exists()
    assert (ROOT / "docs/runbooks/service-scale-support-review.md").exists()


def test_phase25_service_scale_manifest_validates():
    validate(
        load_yaml("meta/service-scale-operations-readiness.yaml"),
        load_json("schema/jsonschema/service-scale-operations-readiness.schema.json"),
    )


def test_phase25_service_scale_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-076")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase25_service_scale_readiness_plan_assets.py -q"
    assert "meta/service-scale-operations-readiness.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-25-service-scale-readiness.yaml")
    assert gate["tests"] == ["TS-076"]
    assert gate["acceptance"] == ["AC-116"]
    assert "meta/service-scale-operations-readiness.yaml" in gate["fixtures"]


def test_phase25_service_scale_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase25_service_scale_operations_readiness.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/service-scale-operations-readiness-report.schema.json"))
    assert report["verdict"] == "pass"
