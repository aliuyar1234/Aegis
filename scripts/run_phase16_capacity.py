#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/capacity-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    slo_profiles = load_yaml("meta/slo-profiles.yaml")
    budget_manifest = load_yaml("meta/performance-budgets.yaml")
    overload_manifest = load_yaml("meta/load-shed-policies.yaml")
    budget_ids = {item["id"] for item in budget_manifest["profiles"]}
    overload_ids = {item["id"] for item in overload_manifest["policies"]}

    results = []
    for profile in slo_profiles["profiles"]:
        verdict = "pass"
        if profile["budget_profile"] not in budget_ids:
            verdict = "fail"
        if profile["overload_policy_ref"] not in overload_ids:
            verdict = "fail"
        if not {"operator_control", "recovery", "effectful_approved"} <= set(profile["protected_classes"]):
            verdict = "fail"
        results.append(
            {
                "profile_id": profile["id"],
                "budget_profile": profile["budget_profile"],
                "overload_policy_ref": profile["overload_policy_ref"],
                "protected_classes": len(profile["protected_classes"]),
                "sli_count": len(profile["slis"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase16-capacity-report",
        "profile_results": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
