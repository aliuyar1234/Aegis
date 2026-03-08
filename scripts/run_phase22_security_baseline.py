#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/security-baseline-manifest.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/security-baseline-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/security-baseline-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    required_ids = {
        "dependency-audit",
        "sbom-generation",
        "secret-scanning",
        "signed-build-artifacts",
        "hardened-defaults",
        "scoped-credentials",
        "key-rotation",
    }

    results = []
    for control in manifest["controls"]:
        verdict = "pass"
        if not all((ROOT / rel).exists() for rel in control["required_refs"]):
            verdict = "fail"
        results.append(
            {
                "control_id": control["id"],
                "ref_count": len(control["required_refs"]),
                "verdict": verdict,
            }
        )

    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and required_ids.issubset({item["id"] for item in manifest["controls"]})

    report = {
        "id": "phase22-security-baseline-report",
        "controls": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
