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


def test_phase18_policy_bundle_docs_exist():
    assert (ROOT / "docs/design-docs/policy-bundles.md").exists()
    assert (ROOT / "docs/runbooks/policy-bundle-rollback.md").exists()


def test_phase18_policy_bundle_manifest_validates():
    validate(
        load_yaml("meta/policy-bundle-profiles.yaml"),
        load_json("schema/jsonschema/policy-bundle-manifest.schema.json"),
    )


def test_phase18_policy_bundle_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-044")

    assert suite["command"] == "pytest tests/policy_bundles -q"
    assert "meta/policy-bundle-profiles.yaml" in suite["paths"]
    assert "scripts/run_phase18_policy_bundles.py" in suite["paths"]


def test_phase18_policy_bundle_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-18-policy-bundles.yaml")

    assert gate["phase"] == "PHASE-18"
    assert gate["tests"] == ["TS-044"]
    assert gate["acceptance"] == ["AC-084"]
    assert "meta/policy-bundle-profiles.yaml" in gate["fixtures"]
    assert "scripts/run_phase18_policy_bundles.py" in gate["fixtures"]


def test_phase18_policy_bundle_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase18_policy_bundles.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/policy-bundle-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["bundles"]) == 2
    assert all(item["dual_control_required"] for item in report["bundles"])
