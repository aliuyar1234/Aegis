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


def test_phase21_onboarding_docs_exist():
    assert (ROOT / "docs/exec-plans/active/PHASE-21-onboarding-and-evaluation-deployment.md").exists()
    assert (ROOT / "docs/design-docs/fresh-clone-onboarding.md").exists()
    assert (ROOT / "docs/runbooks/fresh-clone-first-run.md").exists()


def test_phase21_onboarding_manifest_validates():
    validate(
        load_yaml("meta/fresh-clone-onboarding.yaml"),
        load_json("schema/jsonschema/fresh-clone-onboarding.schema.json"),
    )


def test_phase21_onboarding_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-057")

    assert suite["command"] == "pytest tests/launch_readiness/test_phase21_onboarding_assets.py -q"
    assert "meta/fresh-clone-onboarding.yaml" in suite["paths"]
    assert "scripts/run_phase21_onboarding.py" in suite["paths"]


def test_phase21_onboarding_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-21-fresh-clone-onboarding.yaml")

    assert gate["phase"] == "PHASE-21"
    assert gate["tests"] == ["TS-057"]
    assert gate["acceptance"] == ["AC-097"]
    assert "meta/fresh-clone-onboarding.yaml" in gate["fixtures"]
    assert "scripts/run_phase21_onboarding.py" in gate["fixtures"]


def test_phase21_onboarding_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase21_onboarding.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/fresh-clone-onboarding-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["checks"]) >= 5
