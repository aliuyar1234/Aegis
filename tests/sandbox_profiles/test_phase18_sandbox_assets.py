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


def test_phase18_sandbox_docs_exist():
    assert (ROOT / "docs/design-docs/sandbox-profiles.md").exists()
    assert (ROOT / "docs/runbooks/revoking-extension.md").exists()


def test_phase18_sandbox_manifest_validates():
    validate(
        load_yaml("meta/sandbox-profiles.yaml"),
        load_json("schema/jsonschema/sandbox-profiles.schema.json"),
    )


def test_phase18_sandbox_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-043")

    assert suite["command"] == "pytest tests/sandbox_profiles -q"
    assert "meta/sandbox-profiles.yaml" in suite["paths"]
    assert "scripts/run_phase18_sandbox_profiles.py" in suite["paths"]


def test_phase18_sandbox_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-18-sandbox-profiles.yaml")

    assert gate["phase"] == "PHASE-18"
    assert gate["tests"] == ["TS-043"]
    assert gate["acceptance"] == ["AC-083"]
    assert "meta/sandbox-profiles.yaml" in gate["fixtures"]
    assert "scripts/run_phase18_sandbox_profiles.py" in gate["fixtures"]


def test_phase18_sandbox_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase18_sandbox_profiles.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/sandbox-profile-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["assessments"]) == 6
    assert sum(1 for item in report["assessments"] if item["kind"] == "mcp_adapter") == 2
