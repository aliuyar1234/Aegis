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


def test_phase19_adoption_profile_docs_exist():
    assert (ROOT / "docs/exec-plans/active/PHASE-19-reference-adoption-golden-paths.md").exists()
    assert (ROOT / "docs/design-docs/adoption-profiles.md").exists()
    assert (ROOT / "docs/runbooks/first-adopter-onboarding.md").exists()


def test_phase19_adoption_profile_manifest_validates():
    validate(
        load_yaml("meta/adoption-profiles.yaml"),
        load_json("schema/jsonschema/adoption-profiles.schema.json"),
    )


def test_phase19_adoption_profile_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-047")

    assert suite["command"] == "pytest tests/adoption/test_phase19_adoption_profiles_assets.py -q"
    assert "meta/adoption-profiles.yaml" in suite["paths"]
    assert "scripts/run_phase19_adoption_profiles.py" in suite["paths"]


def test_phase19_adoption_profile_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-19-adoption-profiles.yaml")

    assert gate["phase"] == "PHASE-19"
    assert gate["tests"] == ["TS-047"]
    assert gate["acceptance"] == ["AC-087"]
    assert "meta/adoption-profiles.yaml" in gate["fixtures"]
    assert "scripts/run_phase19_adoption_profiles.py" in gate["fixtures"]


def test_phase19_adoption_profile_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase19_adoption_profiles.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/adoption-profile-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["profiles"]) == 2
    assert all(item["exercise_count"] >= 1 for item in report["profiles"])
