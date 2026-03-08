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


def test_phase25_repeatable_rollout_docs_exist():
    assert (ROOT / "docs/design-docs/repeatable-customer-rollout.md").exists()
    assert (ROOT / "docs/operations/customer-rollout.md").exists()
    assert (ROOT / "docs/runbooks/rollout-cohort-admission.md").exists()


def test_phase25_repeatable_rollout_manifest_validates():
    validate(
        load_yaml("meta/repeatable-customer-rollout.yaml"),
        load_json("schema/jsonschema/repeatable-customer-rollout.schema.json"),
    )


def test_phase25_repeatable_rollout_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-074")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase25_repeatable_rollout_program_plan_assets.py -q"
    assert "meta/repeatable-customer-rollout.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-25-repeatable-rollout-program.yaml")
    assert gate["tests"] == ["TS-074"]
    assert gate["acceptance"] == ["AC-114"]
    assert "meta/repeatable-customer-rollout.yaml" in gate["fixtures"]


def test_phase25_repeatable_rollout_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase25_repeatable_rollout_program.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/repeatable-customer-rollout-report.schema.json"))
    assert report["verdict"] == "pass"
