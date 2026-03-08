#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/real-infrastructure-proving.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/real-infrastructure-proving-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/real-infrastructure-proving.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    track_ids = {item["id"] for item in load_yaml("meta/reference-deployment-tracks.yaml")["tracks"]}
    restore_ids = {item["id"] for item in load_yaml("meta/restore-drill-fixtures.yaml")["drills"]}
    upgrade_ids = {item["id"] for item in load_yaml("meta/upgrade-drill-fixtures.yaml")["drills"]}

    results = []
    proof_refs = set()
    for environment in manifest["environments"]:
        verdict = "pass"
        if environment["deployment_track"] not in track_ids:
            verdict = "fail"
        if environment["restore_drill_id"] not in restore_ids:
            verdict = "fail"
        if environment["upgrade_drill_id"] not in upgrade_ids:
            verdict = "fail"
        if not all((ROOT / rel).exists() for rel in environment["proof_refs"] + environment["runbook_refs"]):
            verdict = "fail"
        proof_refs.update(environment["proof_refs"])
        results.append(
            {
                "environment_id": environment["id"],
                "proof_count": len(environment["proof_refs"]),
                "runbook_count": len(environment["runbook_refs"]),
                "verdict": verdict,
            }
        )

    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and "meta/dedicated-tenant-evidence.yaml" in proof_refs

    report = {
        "id": "phase23-real-infrastructure-proving-report",
        "environments": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
