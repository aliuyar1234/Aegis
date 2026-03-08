#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/service-scale-operations-readiness.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/service-scale-operations-readiness-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/service-scale-operations-readiness.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    rotation_ids = {item["id"] for item in load_yaml("meta/support-model.yaml")["rotations"]}
    results = []
    for cadence in manifest["cadences"]:
        verdict = "pass"
        if cadence["owning_rotation"] not in rotation_ids:
            verdict = "fail"
        if not set(cadence["escalation_rotations"]).issubset(rotation_ids):
            verdict = "fail"
        if not all((ROOT / rel).exists() for rel in cadence["required_refs"]):
            verdict = "fail"
        results.append(
            {
                "cadence_id": cadence["id"],
                "ref_count": len(cadence["required_refs"]),
                "verdict": verdict,
            }
        )

    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and len({item["owning_rotation"] for item in manifest["cadences"]}) >= 3

    report = {
        "id": "phase25-service-scale-operations-readiness-report",
        "cadences": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
