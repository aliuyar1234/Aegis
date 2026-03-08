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


def test_phase20_deprecation_docs_exist():
    assert (ROOT / "docs/design-docs/deprecation-governance.md").exists()
    assert (ROOT / "docs/runbooks/extension-sunset.md").exists()


def test_phase20_deprecation_manifest_validates():
    validate(
        load_yaml("meta/deprecation-governance.yaml"),
        load_json("schema/jsonschema/deprecation-governance.schema.json"),
    )


def test_phase20_deprecation_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-055")

    assert suite["command"] == "pytest tests/lifecycle/test_phase20_deprecation_assets.py -q"
    assert "meta/deprecation-governance.yaml" in suite["paths"]
    assert "scripts/run_phase20_deprecation.py" in suite["paths"]


def test_phase20_deprecation_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-20-deprecation-governance.yaml")

    assert gate["phase"] == "PHASE-20"
    assert gate["tests"] == ["TS-055"]
    assert gate["acceptance"] == ["AC-095"]
    assert "meta/deprecation-governance.yaml" in gate["fixtures"]
    assert "scripts/run_phase20_deprecation.py" in gate["fixtures"]


def test_phase20_deprecation_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase20_deprecation.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/deprecation-governance-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["policies"]) == 3
    assert all(item["asset_count"] >= 1 for item in report["policies"])
