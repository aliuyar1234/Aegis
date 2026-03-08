#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/customer-environment-readiness.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/customer-environment-readiness-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/customer-environment-readiness.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    required_items = {"dns", "certificates", "secrets", "storage", "backups", "alerts", "operational_responsibilities"}
    covered = set()
    results = []

    for section in manifest["check_sections"]:
        verdict = "pass"
        if not all((ROOT / rel).exists() for rel in section["doc_refs"] + section["runbook_refs"]):
            verdict = "fail"
        covered.update(section["required_items"])
        results.append(
            {
                "section_id": section["id"],
                "item_count": len(section["required_items"]),
                "verdict": verdict,
            }
        )

    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and required_items.issubset(covered)

    report = {
        "id": "phase23-customer-environment-readiness-report",
        "sections": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
