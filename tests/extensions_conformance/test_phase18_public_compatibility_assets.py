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


def test_phase18_public_compatibility_docs_exist():
    assert (ROOT / "docs/design-docs/public-compatibility-leadership.md").exists()
    assert (ROOT / "meta/public-benchmark-manifest.yaml").exists()


def test_phase18_public_compatibility_manifest_validates():
    validate(
        load_yaml("meta/public-benchmark-manifest.yaml"),
        load_json("schema/jsonschema/public-benchmark-manifest.schema.json"),
    )


def test_phase18_public_compatibility_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-045")

    assert suite["command"] == "pytest tests/extensions_conformance/test_phase18_public_compatibility_assets.py -q"
    assert "meta/public-benchmark-manifest.yaml" in suite["paths"]
    assert "docs/generated/phase-14-benchmark-scorecard.json" in suite["paths"]


def test_phase18_public_compatibility_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-18-public-compatibility.yaml")

    assert gate["phase"] == "PHASE-18"
    assert gate["tests"] == ["TS-045"]
    assert gate["acceptance"] == ["AC-085"]
    assert "meta/public-benchmark-manifest.yaml" in gate["fixtures"]
    assert "scripts/run_phase18_public_compatibility.py" in gate["fixtures"]


def test_phase18_public_compatibility_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase18_public_compatibility.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/public-compatibility-report.schema.json"))
    assert report["verdict"] == "pass"
    assert report["tracks"][0]["published_case_count"] > 0
    assert report["tracks"][0]["compatibility_dimension_count"] == 4
