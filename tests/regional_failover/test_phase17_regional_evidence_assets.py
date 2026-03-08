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


def test_phase17_evidence_artifacts_exist_and_validate():
    validate(load_yaml("meta/regional-evidence-manifest.yaml"), load_json("schema/jsonschema/regional-evidence-manifest.schema.json"))
    assert (ROOT / "schema/jsonschema/regional-evidence-bundle.schema.json").exists()
    assert (ROOT / "scripts/build_phase17_regional_evidence.py").exists()
    assert (ROOT / "docs/generated/phase-17-regional-evidence.json").exists()


def test_phase17_evidence_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-041")

    assert suite["command"] == "pytest tests/regional_failover/test_phase17_regional_evidence_assets.py -q"
    assert "meta/regional-evidence-manifest.yaml" in suite["paths"]
    assert "docs/generated/phase-17-regional-evidence.json" in suite["paths"]


def test_phase17_evidence_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-17-regional-evidence.yaml")

    assert gate["phase"] == "PHASE-17"
    assert gate["tests"] == ["TS-041"]
    assert gate["acceptance"] == ["AC-081"]
    assert "meta/regional-evidence-manifest.yaml" in gate["fixtures"]
    assert "docs/generated/phase-17-regional-evidence.json" in gate["fixtures"]


def test_phase17_evidence_builder_reproduces_committed_bundle():
    completed = subprocess.run(
        [sys.executable, "scripts/build_phase17_regional_evidence.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    bundle = json.loads(completed.stdout)
    validate(bundle, load_json("schema/jsonschema/regional-evidence-bundle.schema.json"))
    committed = load_json("docs/generated/phase-17-regional-evidence.json")
    assert bundle == committed
    assert bundle["verdict"] == "pass"
    assert len(bundle["reports"]) == 4
