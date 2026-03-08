#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/regional-topology-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    profiles = load_yaml("meta/regional-topology-profiles.yaml")["profiles"]
    domains = load_yaml("meta/fault-domain-catalog.yaml")["domains"]

    profile_results = []
    for profile in profiles:
        verdict = "pass"
        if profile["authoritative_region"] != profile["primary_region"]:
            verdict = "fail"
        if not profile["standby_regions"]:
            verdict = "fail"
        profile_results.append(
            {
                "profile_id": profile["id"],
                "standby_count": len(profile["standby_regions"]),
                "precondition_count": len(profile["promotion_preconditions"]),
                "verdict": verdict,
            }
        )

    domain_results = []
    for domain in domains:
        verdict = "pass"
        if domain["standby_eligible"] and "standby" not in domain["role"]:
            verdict = "fail"
        domain_results.append(
            {
                "domain_id": domain["id"],
                "region": domain["region"],
                "standby_eligible": domain["standby_eligible"],
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase17-regional-topology-report",
        "profile_results": profile_results,
        "domain_results": domain_results,
        "verdict": (
            "pass"
            if all(item["verdict"] == "pass" for item in profile_results + domain_results)
            else "fail"
        ),
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
