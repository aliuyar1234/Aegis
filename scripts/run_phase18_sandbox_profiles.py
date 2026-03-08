#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
PROFILES_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/sandbox-profiles.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/sandbox-profile-report.schema.json").read_text(encoding="utf-8")
)
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/connector-manifest.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    profiles = load_yaml("meta/sandbox-profiles.yaml")
    validate(instance=profiles, schema=PROFILES_SCHEMA)
    profile_map = {profile["id"]: profile for profile in profiles["profiles"]}

    assessments = []
    for assignment in profiles["assignments"]:
        manifest_path = ROOT / assignment["manifest_ref"]
        payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        validate(instance=payload, schema=MANIFEST_SCHEMA)

        profile = profile_map[assignment["profile"]]
        network_mode = payload["capability_boundary"]["network"]["mode"]
        secret_count = len(payload["capability_boundary"]["secrets"])
        artifact_outputs = payload["capability_boundary"]["artifact_access"]["outputs"]
        verdict = "pass"

        if payload["kind"] not in profile["allowed_kinds"]:
            verdict = "fail"
        if payload["sdk"]["language"] not in profile["allowed_sdk_languages"]:
            verdict = "fail"
        if network_mode not in profile["network_modes"]:
            verdict = "fail"
        if secret_count > profile["max_secret_count"]:
            verdict = "fail"
        if payload["kind"] == "mcp_adapter" and not profile["mcp_allowed"]:
            verdict = "fail"
        if profile["requires_artifact_outputs"] and not artifact_outputs:
            verdict = "fail"

        assessments.append(
            {
                "manifest_id": payload["id"],
                "profile_id": profile["id"],
                "kind": payload["kind"],
                "network_mode": network_mode,
                "secret_count": secret_count,
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase18-sandbox-profile-report",
        "assessments": assessments,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in assessments) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
