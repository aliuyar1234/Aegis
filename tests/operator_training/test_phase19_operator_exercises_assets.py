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


def test_phase19_operator_exercise_docs_exist():
    assert (ROOT / "docs/design-docs/operator-exercises.md").exists()
    assert (ROOT / "docs/runbooks/operator-training-exercise.md").exists()


def test_phase19_operator_exercise_manifest_validates():
    validate(
        load_yaml("meta/operator-exercise-manifest.yaml"),
        load_json("schema/jsonschema/operator-exercise-manifest.schema.json"),
    )


def test_phase19_operator_exercise_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-049")

    assert suite["command"] == "pytest tests/operator_training -q"
    assert "meta/operator-exercise-manifest.yaml" in suite["paths"]
    assert "scripts/run_phase19_operator_exercises.py" in suite["paths"]


def test_phase19_operator_exercise_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-19-operator-exercises.yaml")

    assert gate["phase"] == "PHASE-19"
    assert gate["tests"] == ["TS-049"]
    assert gate["acceptance"] == ["AC-089"]
    assert "meta/operator-exercise-manifest.yaml" in gate["fixtures"]
    assert "scripts/run_phase19_operator_exercises.py" in gate["fixtures"]


def test_phase19_operator_exercise_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase19_operator_exercises.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/operator-exercise-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["exercises"]) == 3
    assert all(item["outcome_count"] >= 2 for item in report["exercises"])
