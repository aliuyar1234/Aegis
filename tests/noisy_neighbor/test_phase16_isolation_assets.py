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


def test_phase16_isolation_artifacts_exist_and_validate():
    validate(load_yaml("meta/isolation-profiles.yaml"), load_json("schema/jsonschema/isolation-profiles.schema.json"))
    assert (ROOT / "docs/design-docs/isolation-profiles.md").exists()
    assert (ROOT / "docs/runbooks/hot-tenant-isolation.md").exists()
    assert (ROOT / "scripts/run_phase16_isolation.py").exists()


def test_phase16_isolation_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-034")

    assert suite["command"] == "pytest tests/noisy_neighbor -q"
    assert "meta/isolation-profiles.yaml" in suite["paths"]
    assert "docs/runbooks/hot-tenant-isolation.md" in suite["paths"]


def test_phase16_isolation_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-16-isolation.yaml")

    assert gate["phase"] == "PHASE-16"
    assert gate["tests"] == ["TS-034"]
    assert gate["acceptance"] == ["AC-074"]
    assert "meta/isolation-profiles.yaml" in gate["fixtures"]


def test_phase16_isolation_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase16_isolation.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/isolation-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["scenario_results"]) == 3
