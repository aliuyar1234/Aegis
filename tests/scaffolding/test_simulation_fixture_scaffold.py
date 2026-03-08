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


def test_scaffold_runbook_and_script_exist():
    required_paths = [
        "docs/runbooks/author-simulation-fixture.md",
        "scripts/scaffold_simulation_fixture.py",
        "schema/jsonschema/simulation-scenario.schema.json",
        "schema/jsonschema/simulation-result.schema.json",
    ]

    for path in required_paths:
        assert (ROOT / path).exists(), path


def test_phase14_suite_registry_matches_fixture_scaffold_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-024")

    assert suite["command"] == "pytest tests/scaffolding -q"
    assert "tests/scaffolding" in suite["paths"]
    assert "docs/runbooks/author-simulation-fixture.md" in suite["paths"]
    assert "scripts/scaffold_simulation_fixture.py" in suite["paths"]
    assert "schema/jsonschema/simulation-scenario.schema.json" in suite["paths"]


def test_runbook_makes_manual_registration_boundary_explicit():
    runbook = (ROOT / "docs/runbooks/author-simulation-fixture.md").read_text(encoding="utf-8").lower()

    assert "does not auto-register" in runbook
    assert "meta/simulation-scenarios.yaml" in runbook
    assert "python scripts/run_simulation_scenario.py" in runbook


def test_scaffolded_fixture_validates_and_runs_end_to_end(tmp_path):
    output = tmp_path / "scaffolded-scenario.yaml"
    subprocess.run(
        [
            sys.executable,
            "scripts/scaffold_simulation_fixture.py",
            str(output),
            "--scenario-id",
            "scaffolded-scenario",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    scenario = yaml.safe_load(output.read_text(encoding="utf-8"))
    validate(scenario, load_schema("schema/jsonschema/simulation-scenario.schema.json"))

    completed = subprocess.run(
        [sys.executable, "scripts/run_simulation_scenario.py", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    validate(result, load_schema("schema/jsonschema/simulation-result.schema.json"))
    assert result["scenario_id"] == "scaffolded-scenario"
    assert result["terminal_state"]["replay_equivalent"] is True
