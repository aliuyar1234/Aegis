#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/customer-feedback-loop.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/customer-feedback-loop-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/customer-feedback-loop.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    results = []
    decision_classes = set()
    for channel in manifest["channels"]:
        verdict = "pass"
        if not all((ROOT / rel).exists() for rel in channel["evidence_refs"] + channel["runbook_refs"]):
            verdict = "fail"
        decision_classes.add(channel["decision_class"])
        results.append(
            {
                "channel_id": channel["id"],
                "evidence_count": len(channel["evidence_refs"]),
                "verdict": verdict,
            }
        )

    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and {"operational_fix", "rollout_learning", "launch_exception"}.issubset(decision_classes)

    report = {
        "id": "phase24-customer-feedback-loop-report",
        "channels": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
