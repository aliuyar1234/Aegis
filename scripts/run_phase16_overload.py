#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/load-shed-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    policies = load_yaml("meta/load-shed-policies.yaml")["policies"]
    results = []
    required_protected = {"operator_control", "recovery", "effectful_approved"}
    for policy in policies:
        verdict = "pass"
        if not required_protected <= set(policy["protected_classes"]):
            verdict = "fail"
        if len(policy["actions"]) < 2:
            verdict = "fail"
        if {action["decision"] for action in policy["actions"]} != {"delay", "reject"}:
            verdict = "fail"
        results.append(
            {
                "policy_id": policy["id"],
                "protected_classes": len(policy["protected_classes"]),
                "shed_classes": len(policy["shed_classes"]),
                "action_count": len(policy["actions"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase16-load-shed-report",
        "policy_results": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
