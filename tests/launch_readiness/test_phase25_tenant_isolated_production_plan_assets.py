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


def test_phase25_tenant_isolated_production_docs_exist():
    assert (ROOT / "docs/design-docs/tenant-isolated-production-readiness.md").exists()
    assert (ROOT / "docs/operations/customer-rollout.md").exists()
    assert (ROOT / "docs/runbooks/tenant-production-cutover.md").exists()


def test_phase25_tenant_isolated_production_manifest_validates():
    validate(
        load_yaml("meta/tenant-isolated-production-readiness.yaml"),
        load_json("schema/jsonschema/tenant-isolated-production-readiness.schema.json"),
    )


def test_phase25_tenant_isolated_production_suite_and_gate_references_assets():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-075")
    assert suite["command"] == "pytest tests/launch_readiness/test_phase25_tenant_isolated_production_plan_assets.py -q"
    assert "meta/tenant-isolated-production-readiness.yaml" in suite["paths"]
    gate = load_yaml("tests/phase-gates/phase-25-tenant-isolated-production-readiness.yaml")
    assert gate["tests"] == ["TS-075"]
    assert gate["acceptance"] == ["AC-115"]
    assert "meta/tenant-isolated-production-readiness.yaml" in gate["fixtures"]


def test_phase25_tenant_isolated_production_runner_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/run_phase25_tenant_isolated_production_readiness.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    validate(report, load_json("schema/jsonschema/tenant-isolated-production-readiness-report.schema.json"))
    assert report["verdict"] == "pass"
