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


def test_phase16_capacity_artifacts_exist_and_validate():
    validate(load_yaml("meta/slo-profiles.yaml"), load_json("schema/jsonschema/slo-profiles.schema.json"))
    validate(load_yaml("meta/performance-budgets.yaml"), load_json("schema/jsonschema/performance-budgets.schema.json"))
    validate(load_yaml("meta/load-shed-policies.yaml"), load_json("schema/jsonschema/load-shed-policies.schema.json"))
    assert (ROOT / "docs/design-docs/capacity-model.md").exists()
    assert (ROOT / "scripts/run_phase16_capacity.py").exists()
    assert (ROOT / "schema/jsonschema/capacity-report.schema.json").exists()


def test_phase16_capacity_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-031")

    assert suite["command"] == "pytest tests/performance/test_phase16_capacity_assets.py -q"
    assert "meta/slo-profiles.yaml" in suite["paths"]
    assert "meta/performance-budgets.yaml" in suite["paths"]
    assert "meta/load-shed-policies.yaml" in suite["paths"]
    assert "scripts/run_phase16_capacity.py" in suite["paths"]


def test_phase16_capacity_gate_references_concrete_assets():
    gate = load_yaml("tests/phase-gates/phase-16-capacity-budgets.yaml")
    fixtures = set(gate["fixtures"])
    step_ids = {step["id"] for step in gate["steps"]}

    assert gate["phase"] == "PHASE-16"
    assert gate["tests"] == ["TS-031"]
    assert gate["acceptance"] == ["AC-071"]
    assert "meta/slo-profiles.yaml" in fixtures
    assert "meta/performance-budgets.yaml" in fixtures
    assert "meta/load-shed-policies.yaml" in fixtures
    assert {"slo-profiles", "budget-profiles", "overload-links"} <= step_ids


def test_phase16_capacity_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase16_capacity.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/capacity-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["profile_results"]) == 3
