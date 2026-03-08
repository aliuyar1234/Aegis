#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/tenant-isolated-production-readiness.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/tenant-isolated-production-readiness-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/tenant-isolated-production-readiness.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    track_ids = {item["id"] for item in load_yaml("meta/reference-deployment-tracks.yaml")["tracks"]}
    results = []
    for boundary in manifest["boundaries"]:
        verdict = "pass"
        if boundary["deployment_track"] not in track_ids:
            verdict = "fail"
        if not all((ROOT / rel).exists() for rel in boundary["required_evidence"] + boundary["migration_boundary_refs"] + boundary["rollback_runbook_refs"]):
            verdict = "fail"
        results.append(
            {
                "boundary_id": boundary["id"],
                "evidence_count": len(boundary["required_evidence"]),
                "rollback_count": len(boundary["rollback_runbook_refs"]),
                "verdict": verdict,
            }
        )

    classes = {item["isolation_class"] for item in manifest["boundaries"]}
    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and "dedicated_tenant" in classes and "promoted_isolated_tenant" in classes

    report = {
        "id": "phase25-tenant-isolated-production-readiness-report",
        "boundaries": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
