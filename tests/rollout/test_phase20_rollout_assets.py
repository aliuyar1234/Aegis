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


def test_phase20_rollout_docs_exist():
    assert (ROOT / "docs/design-docs/rollout-wave-governance.md").exists()
    assert (ROOT / "docs/runbooks/rollout-wave-promotion.md").exists()


def test_phase20_rollout_manifest_validates():
    validate(
        load_yaml("meta/rollout-wave-manifest.yaml"),
        load_json("schema/jsonschema/rollout-wave-manifest.schema.json"),
    )


def test_phase20_rollout_suite_registry_matches_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-053")

    assert suite["command"] == "pytest tests/rollout -q"
    assert "meta/rollout-wave-manifest.yaml" in suite["paths"]
    assert "scripts/run_phase20_rollout_waves.py" in suite["paths"]


def test_phase20_rollout_gate_references_assets():
    gate = load_yaml("tests/phase-gates/phase-20-rollout-waves.yaml")

    assert gate["phase"] == "PHASE-20"
    assert gate["tests"] == ["TS-053"]
    assert gate["acceptance"] == ["AC-093"]
    assert "meta/rollout-wave-manifest.yaml" in gate["fixtures"]
    assert "scripts/run_phase20_rollout_waves.py" in gate["fixtures"]


def test_phase20_rollout_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase20_rollout_waves.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/rollout-wave-report.schema.json"))
    assert report["verdict"] == "pass"
    assert len(report["waves"]) == 2
    assert all(item["promotion_count"] >= 3 for item in report["waves"])
