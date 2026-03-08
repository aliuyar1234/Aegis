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


def test_phase15_release_evidence_gate_exists_and_references_concrete_assets():
    gate = load_yaml("tests/phase-gates/phase-15-release-evidence.yaml")
    fixtures = set(gate["fixtures"])

    assert gate["tests"] == ["TS-030"]
    assert gate["acceptance"] == ["AC-070"]
    assert "meta/compatibility-matrix.yaml" in fixtures
    assert "meta/version-skew-rules.yaml" in fixtures
    assert "meta/upgrade-strategies.yaml" in fixtures
    assert "meta/recovery-objectives.yaml" in fixtures
    assert "docs/generated/phase-15-release-evidence.json" in fixtures
    assert (ROOT / "docs/governance/release-evidence-gates.md").exists()


def test_phase15_suite_registry_matches_release_evidence_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-030")

    assert suite["command"] == "pytest tests/release_evidence -q"
    assert "tests/phase-gates/phase-15-release-evidence.yaml" in suite["paths"]
    assert "docs/governance/release-evidence-gates.md" in suite["paths"]
    assert "docs/generated/phase-15-release-evidence.json" in suite["paths"]


def test_phase15_release_evidence_bundle_reproduces_committed_output():
    completed = subprocess.run(
        [sys.executable, "scripts/build_phase15_release_evidence.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    bundle = json.loads(completed.stdout)
    validate(bundle, load_json("schema/jsonschema/release-evidence-bundle.schema.json"))
    committed = load_json("docs/generated/phase-15-release-evidence.json")
    assert bundle == committed
    assert bundle["verdict"] == "pass"
