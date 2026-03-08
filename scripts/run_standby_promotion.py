#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/standby-promotion-evidence.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/standby-promotion-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml(ROOT / "meta/standby-promotion-evidence.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)
    profiles = {item["id"]: item for item in load_yaml(ROOT / "meta/topology-profiles.yaml")["profiles"]}
    restore_drills = {item["id"] for item in load_yaml(ROOT / "meta/restore-drill-fixtures.yaml")["drills"]}

    results = []
    for promotion in manifest["promotions"]:
        profile_exists = promotion["topology_profile"] in profiles
        restore_exists = promotion["recovery_drill_id"] in restore_drills
        ownership_ok = all(
            (
                promotion["fencing_confirmed"],
                promotion["restore_evidence_confirmed"],
                promotion["single_owner_verified"],
            )
        )
        verdict = "pass" if profile_exists and restore_exists and ownership_ok else "fail"
        results.append(
            {
                "promotion_id": promotion["id"],
                "topology_profile": promotion["topology_profile"],
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase15-standby-promotion-report",
        "promotion_results": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
