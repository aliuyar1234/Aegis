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


def test_phase25_rollout_scorecard_docs_exist():
    assert (ROOT / "docs/design-docs/rollout-scorecards-and-reference-evidence.md").exists()
    assert (ROOT / "docs/operations/service-scale-operations.md").exists()
    assert (ROOT / "docs/runbooks/rollout-scorecard-review.md").exists()


def test_phase25_rollout_scorecard_manifest_validates():
    validate(
        load_yaml("meta/rollout-scorecard-program.yaml"),
        load_json("schema/jsonschema/rollout-scorecard-program.schema.json"),
    )


def test_phase25_rollout_scorecard_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-077")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase25_rollout_scorecard_plan_assets.py -q"
    assert "meta/rollout-scorecard-program.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-25-rollout-scorecard.yaml")
    assert gate["tests"] == ["TS-077"]
    assert gate["acceptance"] == ["AC-117"]
    assert "meta/rollout-scorecard-program.yaml" in gate["fixtures"]


def test_phase25_rollout_scorecard_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase25_rollout_scorecards.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/rollout-scorecard-report.schema.json"))
    assert report["verdict"] == "pass"
