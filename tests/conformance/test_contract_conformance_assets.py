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


def test_conformance_docs_artifacts_and_runner_exist():
    required_paths = [
        "docs/design-docs/contract-conformance.md",
        "schema/jsonschema/conformance-fixture-manifest.schema.json",
        "schema/jsonschema/conformance-report.schema.json",
        "tests/conformance/fixtures/runtime-contract-conformance.yaml",
        "tests/conformance/fixtures/sample-conformance-report.yaml",
        "scripts/run_contract_conformance.py",
        "tests/phase-gates/phase-14-contract-conformance.yaml",
    ]

    for path in required_paths:
        assert (ROOT / path).exists(), path


def test_conformance_fixtures_validate_against_schemas():
    validate(
        load_yaml("tests/conformance/fixtures/runtime-contract-conformance.yaml"),
        load_schema("schema/jsonschema/conformance-fixture-manifest.schema.json"),
    )
    validate(
        load_yaml("tests/conformance/fixtures/sample-conformance-report.yaml"),
        load_schema("schema/jsonschema/conformance-report.schema.json"),
    )


def test_phase14_suite_registry_matches_conformance_pytest_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-021")

    assert suite["command"] == "pytest tests/conformance -q"
    assert "tests/conformance" in suite["paths"]
    assert "schema/transport-topology.yaml" in suite["paths"]
    assert "docs/design-docs/contract-conformance.md" in suite["paths"]
    assert "tests/phase-gates/phase-14-contract-conformance.yaml" in suite["paths"]


def test_phase14_conformance_gate_references_concrete_assets():
    gate = load_yaml("tests/phase-gates/phase-14-contract-conformance.yaml")
    fixtures = set(gate["fixtures"])
    step_ids = {step["id"] for step in gate["steps"]}

    assert gate["phase"] == "PHASE-14"
    assert set(gate["tests"]) == {"TS-002", "TS-021"}
    assert set(gate["acceptance"]) == {"AC-059", "AC-061"}
    assert "schema/transport-topology.yaml" in fixtures
    assert "schema/proto/aegis/runtime/v1/worker.proto" in fixtures
    assert "scripts/run_contract_conformance.py" in fixtures
    assert {"transport-binding", "lifecycle-surface", "report-validation"} <= step_ids


def test_conformance_doc_and_manifest_keep_lifecycle_boundary_explicit():
    doc = (ROOT / "docs/design-docs/contract-conformance.md").read_text(encoding="utf-8").lower()
    manifest = load_yaml("tests/conformance/fixtures/runtime-contract-conformance.yaml")
    stages = {item["lifecycle_stage"] for item in manifest["fixtures"]}

    assert "dispatch, heartbeat, progress, cancel, and terminal callbacks" in doc
    assert "control plane truth stays authoritative" in doc
    assert stages == {
        "registry",
        "dispatch",
        "cancel",
        "accepted",
        "progress",
        "heartbeat",
        "completed",
        "failed",
        "cancelled",
    }


def test_conformance_runner_validates_manifest_against_transport_topology():
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_contract_conformance.py",
            "tests/conformance/fixtures/runtime-contract-conformance.yaml",
            "tests/conformance/fixtures/sample-conformance-report.yaml",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "validated" in completed.stdout.lower()
