#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/customer-operations-package.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/customer-operations-package-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/customer-operations-package.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    required_categories = {"installation", "deployment", "upgrade", "limits", "failure_modes", "operational_responsibilities"}
    category_ids = set()
    results = []

    for category in manifest["categories"]:
        verdict = "pass"
        if not all((ROOT / rel).exists() for rel in category["doc_refs"] + category["runbook_refs"]):
            verdict = "fail"
        category_ids.add(category["id"])
        results.append(
            {
                "category_id": category["id"],
                "doc_count": len(category["doc_refs"]),
                "verdict": verdict,
            }
        )

    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and required_categories.issubset(category_ids)

    report = {
        "id": "phase23-customer-operations-package-report",
        "categories": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
