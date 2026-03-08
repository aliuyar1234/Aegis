#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/deprecation-governance.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/deprecation-governance-report.schema.json").read_text(
        encoding="utf-8"
    )
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> int:
    manifest = load_yaml("meta/deprecation-governance.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    starter_kit_ids = {
        item["id"] for item in load_yaml("meta/golden-path-starter-kits.yaml")["kits"]
    }
    certified_pack_ids = {
        item["id"] for item in load_yaml("meta/extension-certification-levels.yaml")["candidates"]
    }
    deployment_track_ids = {
        item["id"] for item in load_yaml("meta/reference-deployment-tracks.yaml")["tracks"]
    }

    results = []
    for policy in manifest["policies"]:
        verdict = "pass"
        if policy["asset_kind"] == "starter_kit":
            known_ids = starter_kit_ids
        elif policy["asset_kind"] == "certified_extension_pack":
            known_ids = certified_pack_ids
        else:
            known_ids = deployment_track_ids

        if not set(policy["asset_ids"]).issubset(known_ids):
            verdict = "fail"
        if not all(path_exists(ref) for ref in policy["successor_refs"]):
            verdict = "fail"
        if not path_exists(policy["rollback_runbook_ref"]):
            verdict = "fail"
        if policy["notice_window_days"] <= 0:
            verdict = "fail"

        results.append(
            {
                "policy_id": policy["id"],
                "asset_count": len(policy["asset_ids"]),
                "successor_count": len(policy["successor_refs"]),
                "notice_window_days": policy["notice_window_days"],
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase20-deprecation-governance-report",
        "policies": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
