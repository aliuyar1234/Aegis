#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/pilot-exit-review-manifest.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/pilot-exit-review-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/pilot-exit-review-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    verdict = "pass"
    if not all((ROOT / rel).exists() for rel in manifest["required_inputs"] + manifest["runbook_refs"]):
        verdict = "fail"

    report = {
        "id": "phase24-pilot-exit-review-report",
        "input_count": len(manifest["required_inputs"]),
        "review_section_count": len(manifest["review_sections"]),
        "recommendation_count": len(manifest["recommendation_outcomes"]),
        "verdict": verdict,
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
