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


def test_phase19_reference_track_docs_exist():
    assert (ROOT / "docs/design-docs/reference-deployment-tracks.md").exists()
    assert (ROOT / "docs/runbooks/first-adopter-onboarding.md").exists()
    assert (ROOT / "docs/runbooks/operator-training-exercise.md").exists()


def test_phase19_reference_track_manifest_validates():
    validate(
        load_yaml("meta/reference-deployment-tracks.yaml"),
        load_json("schema/jsonschema/reference-deployment-tracks.schema.json"),
    )


def test_phase19_reference_track_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-048")

    assert suite["command"] == "pytest tests/adoption/test_phase19_reference_tracks_assets.py -q"
    assert "meta/reference-deployment-tracks.yaml" in suite["paths"]
    assert "scripts/run_phase19_reference_tracks.py" in suite["paths"]


def test_phase19_reference_track_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-19-reference-tracks.yaml")

    assert gate["phase"] == "PHASE-19"
    assert gate["tests"] == ["TS-048"]
    assert gate["acceptance"] == ["AC-088"]
    assert "meta/reference-deployment-tracks.yaml" in gate["fixtures"]
    assert "scripts/run_phase19_reference_tracks.py" in gate["fixtures"]


def test_phase19_reference_track_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase19_reference_tracks.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/reference-deployment-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["tracks"]) == 2
    assert all(item["runbook_count"] >= 2 for item in report["tracks"])
