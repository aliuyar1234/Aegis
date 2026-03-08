#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/customer-golden-paths.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/customer-golden-path-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> int:
    manifest = load_yaml("meta/customer-golden-paths.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    kit_ids = {item["id"] for item in load_yaml("meta/golden-path-starter-kits.yaml")["kits"]}
    track_ids = {item["id"] for item in load_yaml("meta/reference-deployment-tracks.yaml")["tracks"]}

    results = []
    for path in manifest["paths"]:
        verdict = "pass"
        if path["starter_kit_id"] not in kit_ids:
            verdict = "fail"
        if path["deployment_track"] not in track_ids:
            verdict = "fail"
        if not all(path_exists(ref) for ref in path["required_evidence"] + path["runbook_refs"]):
            verdict = "fail"
        if not path["replay_required"] or not path["operator_intervention_supported"]:
            verdict = "fail"

        results.append(
            {
                "path_id": path["id"],
                "workflow_class": path["workflow_class"],
                "evidence_count": len(path["required_evidence"]),
                "runbook_count": len(path["runbook_refs"]),
                "verdict": verdict,
            }
        )

    classes = {item["workflow_class"] for item in manifest["paths"]}
    approval_flags = {item["approval_required"] for item in manifest["paths"]}
    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and "read_heavy_browser_operation" in classes and "approval_gated_browser_write" in classes
    overall = overall and approval_flags == {False, True}

    report = {
        "id": "phase22-customer-golden-paths-report",
        "paths": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
