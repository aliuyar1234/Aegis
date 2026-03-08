from pathlib import Path
import json
import subprocess
import sys

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[3]


def load_yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_phase16_storage_artifacts_exist_and_validate():
    validate(load_yaml("meta/storage-growth-fixtures.yaml"), load_json("schema/jsonschema/storage-growth-manifest.schema.json"))
    assert (ROOT / "docs/design-docs/data-plane-scaling.md").exists()
    assert (ROOT / "scripts/run_phase16_storage_scaling.py").exists()


def test_phase16_storage_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-035")

    assert suite["command"] == "pytest tests/performance/storage_growth -q"
    assert "meta/storage-growth-fixtures.yaml" in suite["paths"]
    assert "tests/phase-gates/phase-16-storage-transport.yaml" in suite["paths"]


def test_phase16_storage_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-16-storage-transport.yaml")

    assert gate["phase"] == "PHASE-16"
    assert gate["tests"] == ["TS-035"]
    assert gate["acceptance"] == ["AC-075"]
    assert "meta/storage-growth-fixtures.yaml" in gate["fixtures"]


def test_phase16_storage_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase16_storage_scaling.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/storage-growth-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["scenario_results"]) == 4
