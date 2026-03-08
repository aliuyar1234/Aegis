#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/isolation-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/isolation-profiles.yaml")
    profiles = {profile["id"]: profile for profile in manifest["profiles"]}
    results = []
    for scenario in manifest["scenarios"]:
        profile = profiles.get(scenario["expected_profile"])
        verdict = "pass"
        if profile is None:
            verdict = "fail"
        elif not set(scenario["preserve_classes"]) <= set(profile["preserve_classes"]):
            verdict = "fail"
        results.append(
            {
                "scenario_id": scenario["id"],
                "profile_id": scenario["expected_profile"],
                "preserve_classes": len(scenario["preserve_classes"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase16-isolation-report",
        "scenario_results": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
