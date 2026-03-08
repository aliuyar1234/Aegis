#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/rollout-wave-manifest.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/rollout-wave-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> int:
    manifest = load_yaml("meta/rollout-wave-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    deployment_tracks = {
        item["id"]: item for item in load_yaml("meta/reference-deployment-tracks.yaml")["tracks"]
    }
    accreditation_tracks = {
        item["id"] for item in load_yaml("meta/operator-accreditation.yaml")["tracks"]
    }

    results = []
    for wave in manifest["waves"]:
        verdict = "pass"
        deployment_track = deployment_tracks.get(wave["deployment_track"])
        if deployment_track is None:
            verdict = "fail"
        elif deployment_track["deployment_flavor_id"] != wave["deployment_flavor_id"]:
            verdict = "fail"
        if wave["accreditation_track"] not in accreditation_tracks:
            verdict = "fail"
        if not all(path_exists(ref) for ref in wave["required_evidence"]):
            verdict = "fail"
        if not path_exists(wave["rollback_runbook_ref"]):
            verdict = "fail"
        if not all(path_exists(ref) for ref in wave["customer_notice_refs"]):
            verdict = "fail"

        results.append(
            {
                "wave_id": wave["id"],
                "promotion_count": len(wave["promotion_criteria"]),
                "evidence_count": len(wave["required_evidence"]),
                "notice_count": len(wave["customer_notice_refs"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase20-rollout-wave-report",
        "waves": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
