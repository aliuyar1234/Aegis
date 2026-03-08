#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/public-benchmark-manifest.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/public-compatibility-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def load_json(rel: str) -> object:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def run_report(script_path: str) -> dict:
    completed = subprocess.run(
        [sys.executable, script_path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def main() -> int:
    manifest = load_yaml("meta/public-benchmark-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)
    certification_meta = load_yaml("meta/extension-certification-levels.yaml")
    candidate_map = {candidate["id"]: candidate for candidate in certification_meta["candidates"]}
    policy_bundles = {bundle["id"] for bundle in load_yaml("meta/policy-bundle-profiles.yaml")["bundles"]}
    scorecard = load_json(manifest["scorecard_ref"])
    certification_report = run_report("scripts/run_phase18_certification.py")
    certification_verdicts = {
        item["candidate_id"]: item["verdict"] for item in certification_report["evaluations"]
    }

    tracks = []
    for track in manifest["tracks"]:
        candidate = candidate_map.get(track["candidate_id"])
        verdict = "pass"
        if candidate is None:
            verdict = "fail"
        elif certification_verdicts.get(track["candidate_id"]) != "pass":
            verdict = "fail"
        elif manifest["publication_requirements"]["require_certified_level"] and track["certification_level"] != "certified":
            verdict = "fail"
        elif manifest["publication_requirements"]["require_policy_bundle_ref"] and candidate["policy_bundle"] not in policy_bundles:
            verdict = "fail"
        elif manifest["publication_requirements"]["require_sandbox_profile_ref"] and not candidate["required_profiles"]:
            verdict = "fail"

        tracks.append(
            {
                "track_id": track["id"],
                "candidate_id": track["candidate_id"],
                "certification_level": track["certification_level"],
                "published_case_count": scorecard["summary"]["case_count"] if verdict == "pass" else 0,
                "compatibility_dimension_count": len(track["compatibility_dimensions"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase18-public-compatibility-report",
        "tracks": tracks,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in tracks) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
