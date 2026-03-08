#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/upcaster-fixture-manifest.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/upcaster-coverage-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    fixtures = load_yaml(ROOT / "meta/upcaster-fixtures.yaml")
    validate(instance=fixtures, schema=FIXTURE_SCHEMA)
    matrix = load_yaml(ROOT / "meta/compatibility-matrix.yaml")
    upcasters = load_yaml(ROOT / "meta/upcaster-manifests.yaml")["upcasters"]

    surface_map = {surface["id"]: surface for surface in matrix["surfaces"]}
    upcaster_map = {
        (item["subject_kind"], item["subject_id"], item["from_version"]): item
        for item in upcasters
    }

    results = []
    for fixture in fixtures["fixtures"]:
        surface = surface_map[fixture["subject_id"]]
        supported = fixture["input_version"] in surface["supported_versions"]
        upcaster = upcaster_map.get((fixture["subject_kind"], fixture["subject_id"], fixture["input_version"]))
        resolved_target = upcaster["to_version"] if upcaster else None

        if fixture["expected_outcome"] == "upcast_to_current":
            verdict = "pass" if supported and resolved_target == fixture["expected_target_version"] else "fail"
        else:
            verdict = "pass" if not supported and resolved_target is None else "fail"

        results.append(
            {
                "fixture_id": fixture["id"],
                "resolved_target_version": resolved_target,
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase15-upcaster-coverage-report",
        "fixture_results": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
