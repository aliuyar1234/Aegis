#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/adoption-profiles.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/adoption-profile-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> int:
    manifest = load_yaml("meta/adoption-profiles.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    track_ids = {
        track["id"] for track in load_yaml("meta/reference-deployment-tracks.yaml")["tracks"]
    }
    starter_kits = {
        kit["id"]: kit for kit in load_yaml("meta/golden-path-starter-kits.yaml")["kits"]
    }
    exercise_ids = {
        exercise["id"] for exercise in load_yaml("meta/operator-exercise-manifest.yaml")["exercises"]
    }

    profile_results = []
    for profile in manifest["profiles"]:
        verdict = "pass"
        starter_kit = starter_kits.get(profile["starter_kit"])

        if profile["deployment_track"] not in track_ids:
            verdict = "fail"
        if starter_kit is None:
            verdict = "fail"
        elif starter_kit["deployment_track"] != profile["deployment_track"]:
            verdict = "fail"
        if not set(profile["operator_exercises"]).issubset(exercise_ids):
            verdict = "fail"
        if not path_exists(profile["onboarding_runbook_ref"]):
            verdict = "fail"
        if not all(path_exists(ref) for ref in profile["required_evidence"]):
            verdict = "fail"

        profile_results.append(
            {
                "profile_id": profile["id"],
                "deployment_track": profile["deployment_track"],
                "starter_kit": profile["starter_kit"],
                "evidence_count": len(profile["required_evidence"]),
                "exercise_count": len(profile["operator_exercises"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase19-adoption-profiles-report",
        "profiles": profile_results,
        "verdict": (
            "pass" if all(item["verdict"] == "pass" for item in profile_results) else "fail"
        ),
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
