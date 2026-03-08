#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/upgrade-drill-manifest.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/upgrade-drill-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml(ROOT / "meta/upgrade-drill-fixtures.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)
    strategies = {item["id"]: item for item in load_yaml(ROOT / "meta/upgrade-strategies.yaml")["strategies"]}
    rules = load_yaml(ROOT / "meta/version-skew-rules.yaml")["rules"]
    checkpoint_surface = next(
        surface for surface in load_yaml(ROOT / "meta/compatibility-matrix.yaml")["surfaces"]
        if surface["id"] == "session-checkpoint"
    )

    results = []
    for drill in manifest["drills"]:
        strategy = strategies[drill["strategy_ref"]]
        rule = next(
            item for item in rules
            if drill["component_group"] in item["components"]
        )
        checkpoint_ok = drill["checkpoint_version"] in checkpoint_surface["supported_versions"]
        contract_ok = drill["runtime_contract_version"] == "v1"
        verdict = "pass" if checkpoint_ok and contract_ok and strategy["guarantees"] else "fail"
        results.append(
            {
                "drill_id": drill["id"],
                "strategy_ref": drill["strategy_ref"],
                "skew_rule_id": rule["id"],
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase15-upgrade-drill-report",
        "drill_results": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
