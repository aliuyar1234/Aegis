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


def test_phase20_incident_review_docs_exist():
    assert (ROOT / "docs/design-docs/incident-review-packets.md").exists()
    assert (ROOT / "docs/runbooks/customer-incident-review.md").exists()


def test_phase20_incident_review_manifest_validates():
    validate(
        load_yaml("meta/incident-review-packets.yaml"),
        load_json("schema/jsonschema/incident-review-packets.schema.json"),
    )


def test_phase20_incident_review_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-054")

    assert suite["command"] == "pytest tests/incident_reviews -q"
    assert "meta/incident-review-packets.yaml" in suite["paths"]
    assert "scripts/run_phase20_incident_reviews.py" in suite["paths"]


def test_phase20_incident_review_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-20-incident-reviews.yaml")

    assert gate["phase"] == "PHASE-20"
    assert gate["tests"] == ["TS-054"]
    assert gate["acceptance"] == ["AC-094"]
    assert "meta/incident-review-packets.yaml" in gate["fixtures"]
    assert "scripts/run_phase20_incident_reviews.py" in gate["fixtures"]


def test_phase20_incident_review_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase20_incident_reviews.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/incident-review-packet-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["packets"]) == 3
    assert all(item["follow_up_count"] >= 2 for item in report["packets"])
