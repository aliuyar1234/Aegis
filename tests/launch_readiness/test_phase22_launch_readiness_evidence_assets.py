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


def test_phase22_launch_evidence_manifest_validates():
    validate(
        load_yaml("meta/launch-readiness-evidence-manifest.yaml"),
        load_json("schema/jsonschema/launch-readiness-evidence-manifest.schema.json"),
    )


def test_phase22_launch_evidence_builder_passes():
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_phase22_launch_readiness_evidence.py",
            "--write",
            "docs/generated/phase-22-launch-readiness-evidence.json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    bundle = json.loads(completed.stdout)
    validate(bundle, load_json("schema/jsonschema/launch-readiness-evidence-bundle.schema.json"))
    assert bundle["verdict"] == "pass"
