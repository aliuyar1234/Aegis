#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/pilot-control-room.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/pilot-control-room-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/pilot-control-room.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    results = []
    for role in manifest["roles"]:
        verdict = "pass"
        if not all((ROOT / rel).exists() for rel in role["observability_refs"] + role["runbook_refs"]):
            verdict = "fail"
        results.append(
            {
                "role_id": role["id"],
                "observability_count": len(role["observability_refs"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase24-pilot-control-room-report",
        "roles": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
