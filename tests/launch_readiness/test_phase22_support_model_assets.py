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


def test_phase22_support_model_docs_exist():
    assert (ROOT / "docs/design-docs/support-operating-model.md").exists()
    assert (ROOT / "docs/operations/support.md").exists()


def test_phase22_support_model_manifest_validates():
    validate(
        load_yaml("meta/support-model.yaml"),
        load_json("schema/jsonschema/support-model.schema.json"),
    )


def test_phase22_support_model_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase22_support_model.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/support-model-report.schema.json"))
    assert report["verdict"] == "pass"
