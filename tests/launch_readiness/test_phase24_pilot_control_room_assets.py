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


def test_phase24_pilot_control_room_docs_exist():
    assert (ROOT / "docs/design-docs/pilot-control-room.md").exists()
    assert (ROOT / "docs/operations/pilot-operations.md").exists()
    assert (ROOT / "docs/runbooks/pilot-control-room.md").exists()


def test_phase24_pilot_control_room_manifest_validates():
    validate(
        load_yaml("meta/pilot-control-room.yaml"),
        load_json("schema/jsonschema/pilot-control-room.schema.json"),
    )


def test_phase24_pilot_control_room_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-070")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase24_pilot_control_room_assets.py -q"
    assert "meta/pilot-control-room.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-24-pilot-control-room.yaml")
    assert gate["tests"] == ["TS-070"]
    assert gate["acceptance"] == ["AC-110"]
    assert "meta/pilot-control-room.yaml" in gate["fixtures"]


def test_phase24_pilot_control_room_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase24_pilot_control_room.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/pilot-control-room-report.schema.json"))
    assert report["verdict"] == "pass"
