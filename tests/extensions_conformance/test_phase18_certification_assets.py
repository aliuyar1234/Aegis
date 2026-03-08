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


def test_phase18_certification_docs_exist():
    assert (ROOT / "docs/exec-plans/active/PHASE-18-certified-ecosystem.md").exists()
    assert (ROOT / "docs/design-docs/extension-certification.md").exists()
    assert (ROOT / "docs/runbooks/revoking-extension.md").exists()


def test_phase18_certification_manifest_validates():
    validate(
        load_yaml("meta/extension-certification-levels.yaml"),
        load_json("schema/jsonschema/extension-certification-levels.schema.json"),
    )


def test_phase18_certification_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-042")

    assert suite["command"] == "pytest tests/extensions_conformance/test_phase18_certification_assets.py -q"
    assert "meta/extension-certification-levels.yaml" in suite["paths"]
    assert "scripts/run_phase18_certification.py" in suite["paths"]


def test_phase18_certification_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-18-extension-certification.yaml")

    assert gate["phase"] == "PHASE-18"
    assert gate["tests"] == ["TS-042"]
    assert gate["acceptance"] == ["AC-082"]
    assert "meta/extension-certification-levels.yaml" in gate["fixtures"]
    assert "scripts/run_phase18_certification.py" in gate["fixtures"]


def test_phase18_certification_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase18_certification.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/extension-certification-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["evaluations"]) == 1
    assert report["evaluations"][0]["member_count"] == 3
    assert len(report["evaluations"][0]["signature"]["digest_sha256"]) == 64
