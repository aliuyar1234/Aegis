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


def test_phase16_overload_artifacts_exist_and_validate():
    validate(load_yaml("meta/load-shed-policies.yaml"), load_json("schema/jsonschema/load-shed-policies.schema.json"))
    assert (ROOT / "docs/design-docs/load-shedding.md").exists()
    assert (ROOT / "docs/runbooks/overload-response.md").exists()
    assert (ROOT / "scripts/run_phase16_overload.py").exists()


def test_phase16_overload_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-033")

    assert suite["command"] == "pytest tests/load_shedding -q"
    assert "meta/load-shed-policies.yaml" in suite["paths"]
    assert "docs/runbooks/overload-response.md" in suite["paths"]


def test_phase16_overload_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-16-overload.yaml")

    assert gate["phase"] == "PHASE-16"
    assert gate["tests"] == ["TS-033"]
    assert gate["acceptance"] == ["AC-073"]
    assert "meta/load-shed-policies.yaml" in gate["fixtures"]


def test_phase16_overload_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase16_overload.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/load-shed-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["policy_results"]) == 3
