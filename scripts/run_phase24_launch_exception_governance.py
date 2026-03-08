#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/launch-exception-governance.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/launch-exception-governance-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/launch-exception-governance.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    rotation_ids = {item["id"] for item in load_yaml("meta/support-model.yaml")["rotations"]}
    results = []
    trigger_classes = set()
    for item in manifest["exceptions"]:
        verdict = "pass"
        if not set(item["required_approvals"]).issubset(rotation_ids):
            verdict = "fail"
        if not all((ROOT / rel).exists() for rel in [item["containment_runbook"], item["rollback_boundary"], *item["evidence_refs"]]):
            verdict = "fail"
        trigger_classes.add(item["trigger_class"])
        results.append(
            {
                "exception_id": item["id"],
                "approval_count": len(item["required_approvals"]),
                "verdict": verdict,
            }
        )

    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and {"reliability", "environment", "support"}.issubset(trigger_classes)

    report = {
        "id": "phase24-launch-exception-governance-report",
        "exceptions": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
