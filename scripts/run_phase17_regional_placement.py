#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/regional-placement-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/regional-placement-policies.yaml")
    policies = {item["id"]: item for item in manifest["policies"]}
    topologies = {item["id"]: item for item in load_yaml("meta/regional-topology-profiles.yaml")["profiles"]}
    decisions = []

    for fixture in manifest["decision_fixtures"]:
        policy = policies[fixture["policy_ref"]]
        topology = topologies[policy["topology_profile_ref"]]
        if fixture["topology_state"] == "healthy":
            selected_region = topology["primary_region"]
        else:
            selected_region = topology["standby_regions"][0]
        decisions.append(
            {
                "fixture_id": fixture["id"],
                "selected_region": selected_region,
                "expected_region": fixture["expected_region"],
                "verdict": "pass" if selected_region == fixture["expected_region"] else "fail",
            }
        )

    report = {
        "id": "phase17-regional-placement-report",
        "decisions": decisions,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in decisions) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
