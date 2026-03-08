#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
DECISION_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/placement-decision.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/placement-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def select_pool(pools: list[dict], fixture: dict) -> str | None:
    candidates = [
        pool
        for pool in pools
        if pool["active"]
        and fixture["tenant_tier"] in pool["supported_tiers"]
        and fixture["required_capability"] in pool["capabilities"]
    ]
    local = [pool for pool in candidates if pool["fault_domain"] == fixture["preferred_fault_domain"]]
    if fixture["tenant_tier"] in {"tier-c", "dedicated"}:
        isolated = [pool for pool in local if pool["isolation_mode"] in {"isolated", "dedicated"}]
        if isolated:
            return sorted(isolated, key=lambda item: item["priority"], reverse=True)[0]["id"]
    if local:
        return sorted(local, key=lambda item: item["priority"], reverse=True)[0]["id"]
    if candidates:
        return sorted(candidates, key=lambda item: item["priority"], reverse=True)[0]["id"]
    return None


def main() -> int:
    placement = load_yaml("meta/placement-policies.yaml")
    decisions = []
    for fixture in placement["decision_fixtures"]:
        selected = select_pool(placement["pool_taxonomy"], fixture)
        decision = {
            "fixture_id": fixture["id"],
            "selected_pool": selected,
            "expected_pool": fixture["expected_pool"],
            "verdict": "pass" if selected == fixture["expected_pool"] else "fail",
        }
        validate(instance=decision, schema=DECISION_SCHEMA)
        decisions.append(decision)

    report = {
        "id": "phase16-placement-report",
        "decisions": decisions,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in decisions) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
