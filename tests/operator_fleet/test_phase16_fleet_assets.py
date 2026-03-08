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


def test_phase16_fleet_artifacts_exist_and_validate():
    validate(load_yaml("meta/fleet-triage-manifest.yaml"), load_json("schema/jsonschema/fleet-triage-manifest.schema.json"))
    assert (ROOT / "docs/product-specs/fleet-triage.md").exists()
    assert (ROOT / "docs/runbooks/top-failure-clusters.md").exists()
    assert (ROOT / "scripts/build_phase16_fleet_evidence.py").exists()
    assert (ROOT / "schema/jsonschema/operator-evidence-bundle.schema.json").exists()


def test_phase16_fleet_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-036")

    assert suite["command"] == "pytest tests/operator_fleet -q"
    assert "meta/fleet-triage-manifest.yaml" in suite["paths"]
    assert "docs/generated/phase-16-fleet-evidence.json" in suite["paths"]
    assert "tests/phase-gates/phase-16-fleet-triage.yaml" in suite["paths"]


def test_phase16_fleet_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-16-fleet-triage.yaml")

    assert gate["phase"] == "PHASE-16"
    assert gate["tests"] == ["TS-036"]
    assert gate["acceptance"] == ["AC-076"]
    assert "meta/fleet-triage-manifest.yaml" in gate["fixtures"]
    assert "docs/generated/phase-16-fleet-evidence.json" in gate["fixtures"]


def test_phase16_fleet_builder_reproduces_committed_bundle():
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_phase16_fleet_evidence.py",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    bundle = json.loads(completed.stdout)
    validate(bundle, load_json("schema/jsonschema/operator-evidence-bundle.schema.json"))
    committed = load_json("docs/generated/phase-16-fleet-evidence.json")
    assert bundle == committed
    assert bundle["verdict"] == "pass"
    assert len(bundle["cluster_summaries"]) == 3
