from pathlib import Path
import json
import subprocess
import sys

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def load_schema(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_replay_diff_docs_artifacts_and_runner_exist():
    required_paths = [
        "docs/design-docs/replay-diffing.md",
        "meta/replay-fixtures.yaml",
        "schema/jsonschema/replay-fixture-manifest.schema.json",
        "schema/jsonschema/replay-diff-result.schema.json",
        "scripts/run_replay_diff.py",
        "tests/phase-gates/phase-14-replay-diff.yaml",
    ]

    for path in required_paths:
        assert (ROOT / path).exists(), path


def test_replay_diff_manifest_validates_against_schema():
    validate(
        load_yaml("meta/replay-fixtures.yaml"),
        load_schema("schema/jsonschema/replay-fixture-manifest.schema.json"),
    )


def test_phase14_suite_registry_matches_replay_diff_pytest_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-022")

    assert suite["command"] == "pytest tests/replay_diff -q"
    assert "tests/replay_diff" in suite["paths"]
    assert "meta/replay-fixtures.yaml" in suite["paths"]
    assert "docs/design-docs/replay-diffing.md" in suite["paths"]
    assert "tests/phase-gates/phase-14-replay-diff.yaml" in suite["paths"]


def test_phase14_replay_diff_gate_references_concrete_assets():
    gate = load_yaml("tests/phase-gates/phase-14-replay-diff.yaml")
    fixtures = set(gate["fixtures"])
    step_ids = {step["id"] for step in gate["steps"]}

    assert gate["phase"] == "PHASE-14"
    assert gate["tests"] == ["TS-022"]
    assert set(gate["acceptance"]) == {"AC-057", "AC-059", "AC-062"}
    assert "meta/replay-fixtures.yaml" in fixtures
    assert "scripts/run_replay_diff.py" in fixtures
    assert {"replay-fixture-manifest", "replay-diff-runner", "replay-diff-tests"} <= step_ids


def test_replay_diff_runner_validates_supported_baselines():
    completed = subprocess.run(
        [sys.executable, "scripts/run_replay_diff.py", "meta/replay-fixtures.yaml"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_schema("schema/jsonschema/replay-diff-result.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["fixture_results"]) == 5
