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


def test_phase17_topology_artifacts_exist_and_validate():
    validate(load_yaml("meta/regional-topology-profiles.yaml"), load_json("schema/jsonschema/regional-topology-profiles.schema.json"))
    validate(load_yaml("meta/fault-domain-catalog.yaml"), load_json("schema/jsonschema/fault-domain-catalog.schema.json"))
    assert (ROOT / "docs/design-docs/regional-topology.md").exists()
    assert (ROOT / "docs/design-docs/fault-domain-policy.md").exists()
    assert (ROOT / "scripts/run_phase17_topology.py").exists()


def test_phase17_topology_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-037")

    assert suite["command"] == "pytest tests/regional_failover/test_phase17_topology_assets.py -q"
    assert "meta/regional-topology-profiles.yaml" in suite["paths"]
    assert "meta/fault-domain-catalog.yaml" in suite["paths"]


def test_phase17_topology_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-17-fault-domains.yaml")

    assert gate["phase"] == "PHASE-17"
    assert gate["tests"] == ["TS-037"]
    assert gate["acceptance"] == ["AC-077"]
    assert "meta/regional-topology-profiles.yaml" in gate["fixtures"]
    assert "meta/fault-domain-catalog.yaml" in gate["fixtures"]


def test_phase17_topology_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase17_topology.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/regional-topology-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["profile_results"]) == 2
