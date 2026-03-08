#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/restore-drill-manifest.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/restore-drill-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml(ROOT / "meta/restore-drill-fixtures.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)
    profiles = {item["id"]: item for item in load_yaml(ROOT / "meta/recovery-objectives.yaml")["profiles"]}

    results = []
    for drill in manifest["drills"]:
        profile = profiles[drill["recovery_profile"]]
        within_targets = (
            drill["observed_rto_minutes"] <= profile["rto_target_minutes"]
            and drill["observed_rpo_minutes"] <= profile["rpo_target_minutes"]
        )
        integrity_ok = all(
            (
                drill["event_chain_integrity_verified"],
                drill["checkpoint_references_verified"],
                drill["artifact_inventory_reconciled"],
                drill["replay_tail_applied"],
            )
        )
        verdict = "pass" if within_targets and integrity_ok else "fail"
        results.append(
            {
                "drill_id": drill["id"],
                "recovery_profile": drill["recovery_profile"],
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase15-restore-drill-report",
        "drill_results": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
