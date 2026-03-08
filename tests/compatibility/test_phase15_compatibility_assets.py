from pathlib import Path
import json
import subprocess
import sys

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def load_schema(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_phase15_compatibility_artifacts_exist_and_validate():
    validate(load_yaml("meta/compatibility-matrix.yaml"), load_schema("schema/jsonschema/compatibility-matrix.schema.json"))
    validate(load_yaml("meta/version-skew-rules.yaml"), load_schema("schema/jsonschema/version-skew-rules.schema.json"))
    assert (ROOT / "scripts/run_phase15_compatibility.py").exists()
    assert (ROOT / "schema/jsonschema/compatibility-report.schema.json").exists()
    assert (ROOT / "docs/design-docs/upgrade-compatibility.md").exists()


def test_phase15_suite_registry_matches_compatibility_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-025")

    assert suite["command"] == "pytest tests/compatibility -q"
    assert "meta/compatibility-matrix.yaml" in suite["paths"]
    assert "meta/version-skew-rules.yaml" in suite["paths"]
    assert "docs/design-docs/upgrade-compatibility.md" in suite["paths"]
    assert "scripts/run_phase15_compatibility.py" in suite["paths"]


def test_phase15_compatibility_runner_emits_passing_report():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase15_compatibility.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_schema("schema/jsonschema/compatibility-report.schema.json"))
    assert report["verdict"] == "pass"
