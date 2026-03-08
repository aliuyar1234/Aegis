#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/session-mobility-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    scenarios = load_yaml("meta/session-mobility-manifest.yaml")["scenarios"]
    results = []
    for scenario in scenarios:
        continuity_count = 0
        if scenario["checkpoint_continuity"] == "required":
            continuity_count += 1
        if scenario["approval_continuity"]:
            continuity_count += 1
        if "preserved" in scenario["artifact_continuity"]:
            continuity_count += 1
        results.append(
            {
                "scenario_id": scenario["id"],
                "expected_authoritative_region": scenario["expected_authoritative_region"],
                "continuity_count": continuity_count,
                "verdict": "pass" if continuity_count == 3 and scenario["expected_authoritative_region"] == scenario["target_region"] else "fail",
            }
        )

    report = {
        "id": "phase17-session-mobility-report",
        "scenario_results": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
