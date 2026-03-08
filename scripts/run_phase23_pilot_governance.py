#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/pilot-governance-manifest.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/pilot-governance-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/pilot-governance-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    refs = manifest["launch_decision_inputs"] + manifest["docs_refs"] + manifest["runbook_refs"]
    verdict = "pass" if all((ROOT / rel).exists() for rel in refs) else "fail"
    if manifest["pilot"]["max_design_partners"] < 1:
        verdict = "fail"

    report = {
        "id": "phase23-pilot-governance-report",
        "success_criteria_count": len(manifest["success_criteria"]),
        "kill_switch_count": len(manifest["kill_switch_conditions"]),
        "decision_input_count": len(manifest["launch_decision_inputs"]),
        "verdict": verdict,
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
