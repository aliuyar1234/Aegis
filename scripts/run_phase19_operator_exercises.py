#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/operator-exercise-manifest.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/operator-exercise-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> int:
    manifest = load_yaml("meta/operator-exercise-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    known_scenario_types = {
        "approval_and_recovery",
        "regional_failover",
        "ecosystem_revocation",
    }
    results = []
    for exercise in manifest["exercises"]:
        verdict = "pass"
        if exercise["scenario_type"] not in known_scenario_types:
            verdict = "fail"
        if not all(path_exists(ref) for ref in exercise["runbook_refs"]):
            verdict = "fail"
        if not all(path_exists(ref) for ref in exercise["required_evidence"]):
            verdict = "fail"

        results.append(
            {
                "exercise_id": exercise["id"],
                "runbook_count": len(exercise["runbook_refs"]),
                "evidence_count": len(exercise["required_evidence"]),
                "outcome_count": len(exercise["expected_outcomes"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase19-operator-exercise-report",
        "exercises": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
