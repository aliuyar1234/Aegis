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


def test_phase15_topology_artifacts_exist_and_validate():
    validate(load_yaml("meta/topology-profiles.yaml"), load_schema("schema/jsonschema/topology-profiles.schema.json"))
    validate(load_yaml("meta/standby-promotion-evidence.yaml"), load_schema("schema/jsonschema/standby-promotion-evidence.schema.json"))
    gate = load_yaml("tests/phase-gates/phase-15-standby-promotion.yaml")

    assert gate["tests"] == ["TS-029"]
    assert gate["acceptance"] == ["AC-069"]
    assert (ROOT / "scripts/run_standby_promotion.py").exists()
    assert (ROOT / "schema/jsonschema/standby-promotion-report.schema.json").exists()
    assert (ROOT / "docs/design-docs/standby-topology.md").exists()
    assert (ROOT / "docs/runbooks/standby-promotion.md").exists()


def test_phase15_suite_registry_matches_topology_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-029")

    assert suite["command"] == "pytest tests/topology -q"
    assert "meta/topology-profiles.yaml" in suite["paths"]
    assert "tests/phase-gates/phase-15-standby-promotion.yaml" in suite["paths"]
    assert "meta/standby-promotion-evidence.yaml" in suite["paths"]


def test_phase15_standby_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_standby_promotion.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_schema("schema/jsonschema/standby-promotion-report.schema.json"))
    assert report["verdict"] == "pass"
