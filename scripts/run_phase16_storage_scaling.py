#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/storage-growth-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/storage-growth-fixtures.yaml")
    budgets = {item["id"] for item in load_yaml("meta/performance-budgets.yaml")["profiles"]}
    results = []
    for scenario in manifest["scenarios"]:
        verdict = "pass"
        if scenario["budget_profile"] not in budgets:
            verdict = "fail"
        if "archive" not in scenario["retention_strategy"] and "rolling" not in scenario["retention_strategy"]:
            verdict = "fail"
        results.append(
            {
                "scenario_id": scenario["id"],
                "component": scenario["component"],
                "budget_profile": scenario["budget_profile"],
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase16-storage-growth-report",
        "scenario_results": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
