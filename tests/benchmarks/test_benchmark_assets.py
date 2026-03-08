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


def test_benchmark_docs_artifacts_and_runner_exist():
    required_paths = [
        "benchmarks/README.md",
        "docs/design-docs/benchmark-corpus.md",
        "docs/generated/phase-14-benchmark-scorecard.json",
        "meta/benchmark-corpus.yaml",
        "meta/performance-budgets.yaml",
        "schema/jsonschema/benchmark-corpus.schema.json",
        "schema/jsonschema/performance-budgets.schema.json",
        "schema/jsonschema/benchmark-run.schema.json",
        "schema/jsonschema/benchmark-scorecard.schema.json",
        "scripts/run_benchmark_corpus.py",
        "tests/phase-gates/phase-14-benchmark-scorecard.yaml",
    ]

    for path in required_paths:
        assert (ROOT / path).exists(), path


def test_benchmark_inputs_validate_against_schemas():
    validate(
        load_yaml("meta/benchmark-corpus.yaml"),
        load_json("schema/jsonschema/benchmark-corpus.schema.json"),
    )
    validate(
        load_yaml("meta/performance-budgets.yaml"),
        load_json("schema/jsonschema/performance-budgets.schema.json"),
    )
    validate(
        load_json("docs/generated/phase-14-benchmark-scorecard.json"),
        load_json("schema/jsonschema/benchmark-scorecard.schema.json"),
    )


def test_phase14_suite_registry_matches_benchmark_pytest_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-023")

    assert suite["command"] == "pytest tests/benchmarks -q"
    assert "tests/benchmarks" in suite["paths"]
    assert "meta/benchmark-corpus.yaml" in suite["paths"]
    assert "meta/performance-budgets.yaml" in suite["paths"]
    assert "docs/generated/phase-14-benchmark-scorecard.json" in suite["paths"]
    assert "tests/phase-gates/phase-14-benchmark-scorecard.yaml" in suite["paths"]


def test_phase14_benchmark_gate_references_concrete_assets():
    gate = load_yaml("tests/phase-gates/phase-14-benchmark-scorecard.yaml")
    fixtures = set(gate["fixtures"])
    step_ids = {step["id"] for step in gate["steps"]}

    assert gate["phase"] == "PHASE-14"
    assert gate["tests"] == ["TS-023"]
    assert gate["acceptance"] == ["AC-063"]
    assert "meta/benchmark-corpus.yaml" in fixtures
    assert "meta/performance-budgets.yaml" in fixtures
    assert "docs/generated/phase-14-benchmark-scorecard.json" in fixtures
    assert {"benchmark-corpus", "budget-profiles", "generated-scorecard"} <= step_ids


def test_benchmark_runner_reproduces_committed_scorecard():
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_benchmark_corpus.py",
            "meta/benchmark-corpus.yaml",
            "meta/performance-budgets.yaml",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    scorecard = json.loads(completed.stdout)
    validate(scorecard, load_json("schema/jsonschema/benchmark-scorecard.schema.json"))
    committed = load_json("docs/generated/phase-14-benchmark-scorecard.json")
    assert scorecard == committed
    assert scorecard["overall_verdict"] == "pass"
    assert scorecard["summary"]["case_count"] == 5
