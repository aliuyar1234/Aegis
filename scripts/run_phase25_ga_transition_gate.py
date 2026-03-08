#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/ga-transition-gate-manifest.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/ga-transition-gate-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/ga-transition-gate-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    checks = [
        {
            "name": "required-inputs",
            "verdict": "pass" if all((ROOT / rel).exists() for rel in manifest["required_inputs"]) else "fail",
        },
        {
            "name": "required-evidence",
            "verdict": "pass" if all((ROOT / rel).exists() for rel in manifest["required_evidence"]) else "fail",
        },
        {
            "name": "required-runbooks",
            "verdict": "pass" if all((ROOT / rel).exists() for rel in manifest["required_runbooks"]) else "fail",
        },
        {
            "name": "required-targets",
            "verdict": "pass" if all(f"{target}:" in makefile for target in manifest["required_targets"]) else "fail",
        },
        {
            "name": "required-docs",
            "verdict": "pass" if all((ROOT / rel).exists() for rel in manifest["required_docs"]) else "fail",
        },
    ]

    report = {
        "id": "phase25-ga-transition-gate-report",
        "checks": checks,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in checks) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
