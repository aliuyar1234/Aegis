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


def test_phase15_upcaster_artifacts_exist_and_validate():
    validate(load_yaml("meta/upcaster-manifests.yaml"), load_schema("schema/jsonschema/upcaster-manifest.schema.json"))
    validate(load_yaml("meta/upcaster-fixtures.yaml"), load_schema("schema/jsonschema/upcaster-fixture-manifest.schema.json"))
    assert (ROOT / "scripts/run_upcaster_coverage.py").exists()
    assert (ROOT / "schema/jsonschema/upcaster-coverage-report.schema.json").exists()
    assert (ROOT / "docs/design-docs/schema-evolution.md").exists()


def test_phase15_suite_registry_matches_upcaster_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-026")

    assert suite["command"] == "pytest tests/migrations -q"
    assert "meta/upcaster-manifests.yaml" in suite["paths"]
    assert "schema/jsonschema/upcaster-manifest.schema.json" in suite["paths"]
    assert "docs/design-docs/schema-evolution.md" in suite["paths"]
    assert "meta/upcaster-fixtures.yaml" in suite["paths"]


def test_phase15_upcaster_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_upcaster_coverage.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_schema("schema/jsonschema/upcaster-coverage-report.schema.json"))
    assert report["verdict"] == "pass"
