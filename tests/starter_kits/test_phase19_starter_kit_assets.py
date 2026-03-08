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


def test_phase19_starter_kit_docs_exist():
    assert (ROOT / "docs/design-docs/golden-path-starter-kits.md").exists()
    assert (ROOT / "docs/runbooks/first-adopter-onboarding.md").exists()


def test_phase19_starter_kit_manifest_validates():
    validate(
        load_yaml("meta/golden-path-starter-kits.yaml"),
        load_json("schema/jsonschema/golden-path-starter-kits.schema.json"),
    )


def test_phase19_starter_kit_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-050")

    assert suite["command"] == "pytest tests/starter_kits -q"
    assert "meta/golden-path-starter-kits.yaml" in suite["paths"]
    assert "scripts/run_phase19_starter_kits.py" in suite["paths"]


def test_phase19_starter_kit_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-19-starter-kits.yaml")

    assert gate["phase"] == "PHASE-19"
    assert gate["tests"] == ["TS-050"]
    assert gate["acceptance"] == ["AC-090"]
    assert "meta/golden-path-starter-kits.yaml" in gate["fixtures"]
    assert "scripts/run_phase19_starter_kits.py" in gate["fixtures"]


def test_phase19_starter_kit_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase19_starter_kits.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/golden-path-starter-kit-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["kits"]) == 2
    assert all(item["scenario_count"] >= 3 for item in report["kits"])
