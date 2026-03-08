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


def test_phase22_security_baseline_docs_exist():
    assert (ROOT / "docs/design-docs/launch-security-baseline.md").exists()
    assert (ROOT / "docs/runbooks/security-baseline-review.md").exists()


def test_phase22_security_baseline_manifest_validates():
    validate(
        load_yaml("meta/security-baseline-manifest.yaml"),
        load_json("schema/jsonschema/security-baseline-manifest.schema.json"),
    )


def test_phase22_security_baseline_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase22_security_baseline.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/security-baseline-report.schema.json"))
    assert report["verdict"] == "pass"
