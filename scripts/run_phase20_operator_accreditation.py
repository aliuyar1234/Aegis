#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/operator-accreditation.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/operator-accreditation-report.schema.json").read_text(
        encoding="utf-8"
    )
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> int:
    manifest = load_yaml("meta/operator-accreditation.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    track_ids = {
        item["id"] for item in load_yaml("meta/reference-deployment-tracks.yaml")["tracks"]
    }
    exercise_ids = {
        item["id"] for item in load_yaml("meta/operator-exercise-manifest.yaml")["exercises"]
    }

    results = []
    for track in manifest["tracks"]:
        verdict = "pass"
        if not set(track["deployment_tracks"]).issubset(track_ids):
            verdict = "fail"
        if not set(track["required_exercises"]).issubset(exercise_ids):
            verdict = "fail"
        if not all(path_exists(ref) for ref in track["required_evidence"]):
            verdict = "fail"
        if not path_exists(track["runbook_ref"]):
            verdict = "fail"
        if track["renewal_window_days"] <= 0:
            verdict = "fail"

        results.append(
            {
                "track_id": track["id"],
                "exercise_count": len(track["required_exercises"]),
                "evidence_count": len(track["required_evidence"]),
                "deployment_track_count": len(track["deployment_tracks"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase20-operator-accreditation-report",
        "tracks": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
