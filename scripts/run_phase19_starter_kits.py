#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/golden-path-starter-kits.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/golden-path-starter-kit-report.schema.json").read_text(
        encoding="utf-8"
    )
)
PACK_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/extension-pack-manifest.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> int:
    manifest = load_yaml("meta/golden-path-starter-kits.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    candidates = {
        item["id"]: item for item in load_yaml("meta/extension-certification-levels.yaml")["candidates"]
    }
    sandbox_profiles = {
        item["id"] for item in load_yaml("meta/sandbox-profiles.yaml")["profiles"]
    }
    policy_bundles = {
        item["id"] for item in load_yaml("meta/policy-bundle-profiles.yaml")["bundles"]
    }
    scenario_ids = {item["id"] for item in load_yaml("meta/simulation-scenarios.yaml")["scenarios"]}
    public_track_ids = {
        item["id"] for item in load_yaml("meta/public-benchmark-manifest.yaml")["tracks"]
    }
    deployment_track_ids = {
        item["id"] for item in load_yaml("meta/reference-deployment-tracks.yaml")["tracks"]
    }

    results = []
    for kit in manifest["kits"]:
        verdict = "pass"
        candidate = candidates.get(kit["certification_candidate_id"])
        if candidate is None:
            verdict = "fail"
        elif candidate["policy_bundle"] != kit["policy_bundle_id"]:
            verdict = "fail"
        elif candidate["public_track"] != kit["public_track_id"]:
            verdict = "fail"

        if kit["deployment_track"] not in deployment_track_ids:
            verdict = "fail"
        if kit["policy_bundle_id"] not in policy_bundles:
            verdict = "fail"
        if kit["public_track_id"] not in public_track_ids:
            verdict = "fail"
        if not set(kit["required_sandbox_profiles"]).issubset(sandbox_profiles):
            verdict = "fail"
        if not set(kit["simulation_scenarios"]).issubset(scenario_ids):
            verdict = "fail"
        if not all(path_exists(ref) for ref in kit["docs_refs"]):
            verdict = "fail"
        if not path_exists(kit["extension_pack_ref"]):
            verdict = "fail"
        else:
            pack = load_yaml(kit["extension_pack_ref"])
            validate(instance=pack, schema=PACK_SCHEMA)
            if candidate is not None and candidate["pack_ref"] != kit["extension_pack_ref"]:
                verdict = "fail"
        if candidate is not None and not set(kit["required_sandbox_profiles"]).issubset(
            set(candidate["required_profiles"])
        ):
            verdict = "fail"

        results.append(
            {
                "kit_id": kit["id"],
                "scenario_count": len(kit["simulation_scenarios"]),
                "profile_count": len(kit["required_sandbox_profiles"]),
                "doc_count": len(kit["docs_refs"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase19-starter-kit-report",
        "kits": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
