#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/support-model.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/support-model-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/support-model.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    rotation_ids = {item["id"] for item in manifest["rotations"]}
    template_ids = {item["id"] for item in manifest["communication_templates"]}

    last_response = -1
    results = []
    for severity in manifest["severities"]:
        verdict = "pass"
        if severity["owning_rotation"] not in rotation_ids:
            verdict = "fail"
        if not set(severity["escalation_path"]).issubset(rotation_ids):
            verdict = "fail"
        if severity["communication_template"] not in template_ids:
            verdict = "fail"
        if severity["response_minutes"] < last_response:
            verdict = "fail"
        last_response = severity["response_minutes"]
        results.append(
            {
                "severity_id": severity["id"],
                "response_minutes": severity["response_minutes"],
                "verdict": verdict,
            }
        )

    overall = all((ROOT / rel).exists() for rel in manifest["support_docs"])
    overall = overall and all((ROOT / item["doc_ref"]).exists() for item in manifest["communication_templates"])
    overall = overall and all(item["verdict"] == "pass" for item in results)

    report = {
        "id": "phase22-support-model-report",
        "severities": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
