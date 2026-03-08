#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/regional-evacuation-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    drills = load_yaml("meta/regional-evacuation-fixtures.yaml")["drills"]
    results = []
    for drill in drills:
        required = {"fence_primary_region", "validate_restore_evidence", "promote_standby_region"}
        steps = set(drill["expected_steps"])
        if drill["trigger"] == "compliance_driven_relocation":
            required = {"validate_restore_evidence", "promote_target_region", "verify_artifact_lineage"}
        verdict = "pass" if required <= steps else "fail"
        results.append(
            {
                "drill_id": drill["id"],
                "step_count": len(drill["expected_steps"]),
                "source_region": drill["source_region"],
                "target_region": drill["target_region"],
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase17-regional-evacuation-report",
        "drill_results": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
