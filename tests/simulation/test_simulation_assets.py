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


def run_scenario(path: str):
    completed = subprocess.run(
        [sys.executable, "scripts/run_simulation_scenario.py", path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_simulation_docs_artifacts_and_runner_exist():
    required_paths = [
        "docs/design-docs/simulation-lab.md",
        "meta/fault-injection-matrix.yaml",
        "meta/simulation-scenarios.yaml",
        "schema/jsonschema/fault-injection-step.schema.json",
        "schema/jsonschema/fault-injection-matrix.schema.json",
        "schema/jsonschema/simulation-scenario.schema.json",
        "schema/jsonschema/simulation-scenario-manifest.schema.json",
        "schema/jsonschema/simulation-result.schema.json",
        "scripts/run_simulation_scenario.py",
        "tests/phase-gates/phase-14-simulation.yaml",
    ]

    for path in required_paths:
        assert (ROOT / path).exists(), path


def test_simulation_machine_readable_artifacts_validate_against_schemas():
    schema_pairs = [
        ("meta/fault-injection-matrix.yaml", "schema/jsonschema/fault-injection-matrix.schema.json"),
        ("meta/simulation-scenarios.yaml", "schema/jsonschema/simulation-scenario-manifest.schema.json"),
    ]

    for payload_path, schema_path in schema_pairs:
        validate(load_yaml(payload_path), load_schema(schema_path))

    scenario_schema = load_schema("schema/jsonschema/simulation-scenario.schema.json")
    for item in load_yaml("meta/simulation-scenarios.yaml")["scenarios"]:
        validate(load_yaml(item["scenario_ref"]), scenario_schema)


def test_phase14_suite_registry_matches_simulation_pytest_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-020")

    assert suite["command"] == "pytest tests/simulation -q"
    assert "tests/simulation" in suite["paths"]
    assert "meta/fault-injection-matrix.yaml" in suite["paths"]
    assert "meta/simulation-scenarios.yaml" in suite["paths"]
    assert "docs/design-docs/simulation-lab.md" in suite["paths"]
    assert "tests/phase-gates/phase-14-simulation.yaml" in suite["paths"]


def test_phase14_simulation_gate_references_concrete_assets():
    gate = load_yaml("tests/phase-gates/phase-14-simulation.yaml")
    fixtures = set(gate["fixtures"])
    step_ids = {step["id"] for step in gate["steps"]}

    assert gate["phase"] == "PHASE-14"
    assert gate["tests"] == ["TS-020"]
    assert set(gate["acceptance"]) == {"AC-059", "AC-060"}
    assert "meta/fault-injection-matrix.yaml" in fixtures
    assert "meta/simulation-scenarios.yaml" in fixtures
    assert "schema/jsonschema/simulation-result.schema.json" in fixtures
    assert "scripts/run_simulation_scenario.py" in fixtures
    assert {"fault-matrix", "scenario-dsl", "deterministic-runner"} <= step_ids


def test_simulation_docs_and_matrix_make_boundaries_explicit():
    doc = (ROOT / "docs/design-docs/simulation-lab.md").read_text(encoding="utf-8").lower()
    matrix = load_yaml("meta/fault-injection-matrix.yaml")

    assert "it is not a browser emulator" in doc
    assert "the runner never calls browsers, model providers, or external apis" in doc
    assert {item["id"] for item in matrix["faults"]} == {
        "worker_crash",
        "node_loss",
        "approval_timeout",
        "duplicate_callback",
        "browser_instability",
    }


def test_simulation_runner_is_deterministic_for_all_registered_scenarios():
    manifest = load_yaml("meta/simulation-scenarios.yaml")
    result_schema = load_schema("schema/jsonschema/simulation-result.schema.json")

    for scenario in manifest["scenarios"]:
        first = run_scenario(scenario["scenario_ref"])
        second = run_scenario(scenario["scenario_ref"])
        assert first == second
        validate(first, result_schema)
        assert first["scenario_id"] == scenario["id"]
        assert first["result_signature"]
        assert first["terminal_state"]["replay_equivalent"] is True
