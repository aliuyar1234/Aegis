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


def test_phase15_recovery_artifacts_exist_and_validate():
    validate(load_yaml("meta/recovery-objectives.yaml"), load_schema("schema/jsonschema/recovery-objective.schema.json"))
    validate(load_yaml("meta/restore-drill-fixtures.yaml"), load_schema("schema/jsonschema/restore-drill-manifest.schema.json"))
    gate = load_yaml("tests/phase-gates/phase-15-restore-drill.yaml")

    assert gate["tests"] == ["TS-028"]
    assert gate["acceptance"] == ["AC-068"]
    assert (ROOT / "scripts/run_restore_drill.py").exists()
    assert (ROOT / "schema/jsonschema/restore-drill-report.schema.json").exists()
    assert (ROOT / "docs/design-docs/disaster-recovery.md").exists()
    assert (ROOT / "docs/runbooks/pitr-restore.md").exists()


def test_phase15_suite_registry_matches_recovery_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-028")

    assert suite["command"] == "pytest tests/disaster_recovery -q"
    assert "meta/recovery-objectives.yaml" in suite["paths"]
    assert "tests/phase-gates/phase-15-restore-drill.yaml" in suite["paths"]
    assert "meta/restore-drill-fixtures.yaml" in suite["paths"]


def test_phase15_restore_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_restore_drill.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_schema("schema/jsonschema/restore-drill-report.schema.json"))
    assert report["verdict"] == "pass"
