#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/release-signoff-manifest.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/release-signoff-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/release-signoff-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    restore_ids = {item["id"] for item in load_yaml("meta/restore-drill-fixtures.yaml")["drills"]}
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    checks = [
        {
            "name": "evidence-refs",
            "verdict": "pass"
            if all((ROOT / rel).exists() for rel in manifest["required_evidence"])
            else "fail",
        },
        {
            "name": "restore-drill-refs",
            "verdict": "pass"
            if set(manifest["required_restore_drills"]).issubset(restore_ids)
            else "fail",
        },
        {
            "name": "rollback-runbooks",
            "verdict": "pass"
            if all((ROOT / rel).exists() for rel in manifest["required_rollback_runbooks"])
            else "fail",
        },
        {
            "name": "eval-targets",
            "verdict": "pass"
            if all(f"{target}:" in makefile for target in manifest["required_eval_targets"])
            else "fail",
        },
        {
            "name": "required-docs",
            "verdict": "pass"
            if all((ROOT / rel).exists() for rel in manifest["required_docs"])
            else "fail",
        },
    ]

    report = {
        "id": "phase22-release-signoff-report",
        "checks": checks,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in checks) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
