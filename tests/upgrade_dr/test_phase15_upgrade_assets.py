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


def test_phase15_upgrade_artifacts_exist_and_validate():
    validate(load_yaml("meta/upgrade-strategies.yaml"), load_schema("schema/jsonschema/upgrade-strategies.schema.json"))
    validate(load_yaml("meta/upgrade-drill-fixtures.yaml"), load_schema("schema/jsonschema/upgrade-drill-manifest.schema.json"))
    gate = load_yaml("tests/phase-gates/phase-15-rolling-upgrade.yaml")

    assert gate["tests"] == ["TS-027"]
    assert gate["acceptance"] == ["AC-067"]
    assert (ROOT / "scripts/run_upgrade_drill.py").exists()
    assert (ROOT / "schema/jsonschema/upgrade-drill-report.schema.json").exists()
    assert (ROOT / "docs/design-docs/rolling-upgrades.md").exists()
    assert (ROOT / "docs/runbooks/rolling-upgrade.md").exists()


def test_phase15_suite_registry_matches_upgrade_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-027")

    assert suite["command"] == "pytest tests/upgrade_dr -q"
    assert "meta/upgrade-strategies.yaml" in suite["paths"]
    assert "tests/phase-gates/phase-15-rolling-upgrade.yaml" in suite["paths"]
    assert "meta/upgrade-drill-fixtures.yaml" in suite["paths"]


def test_phase15_upgrade_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_upgrade_drill.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_schema("schema/jsonschema/upgrade-drill-report.schema.json"))
    assert report["verdict"] == "pass"
