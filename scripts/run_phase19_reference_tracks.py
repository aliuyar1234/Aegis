#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/reference-deployment-tracks.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/reference-deployment-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> int:
    manifest = load_yaml("meta/reference-deployment-tracks.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    flavor_ids = {item["id"] for item in load_yaml("meta/deployment-flavors.yaml")["flavors"]}
    topology_ids = {item["id"] for item in load_yaml("meta/topology-profiles.yaml")["profiles"]}
    regional_ids = {
        item["id"] for item in load_yaml("meta/regional-topology-profiles.yaml")["profiles"]
    }
    slo_ids = {item["id"] for item in load_yaml("meta/slo-profiles.yaml")["profiles"]}
    public_track_ids = {
        item["id"] for item in load_yaml("meta/public-benchmark-manifest.yaml")["tracks"]
    }

    results = []
    for track in manifest["tracks"]:
        verdict = "pass"
        if track["deployment_flavor_id"] not in flavor_ids:
            verdict = "fail"
        if track["topology_profile_id"] not in topology_ids:
            verdict = "fail"
        if track["regional_topology_profile_id"] not in regional_ids:
            verdict = "fail"
        if track["slo_profile_id"] not in slo_ids:
            verdict = "fail"
        if track["public_track_id"] not in public_track_ids:
            verdict = "fail"
        if not all(path_exists(ref) for ref in track["required_evidence"]):
            verdict = "fail"
        if not all(path_exists(ref) for ref in track["runbook_refs"]):
            verdict = "fail"

        results.append(
            {
                "track_id": track["id"],
                "runbook_count": len(track["runbook_refs"]),
                "evidence_count": len(track["required_evidence"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase19-reference-deployment-report",
        "tracks": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
