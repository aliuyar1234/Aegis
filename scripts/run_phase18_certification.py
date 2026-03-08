#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
CERTIFICATION_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/extension-certification-levels.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/extension-certification-report.schema.json").read_text(encoding="utf-8")
)
PACK_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/extension-pack-manifest.schema.json").read_text(encoding="utf-8")
)
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/connector-manifest.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def digest_paths(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    certification = load_yaml("meta/extension-certification-levels.yaml")
    validate(instance=certification, schema=CERTIFICATION_SCHEMA)

    levels = {level["id"] for level in certification["levels"]}
    policy_bundles = {
        bundle["id"] for bundle in load_yaml("meta/policy-bundle-profiles.yaml")["bundles"]
    }
    sandbox_assignments = {
        str((ROOT / assignment["manifest_ref"]).resolve()): assignment["profile"]
        for assignment in load_yaml("meta/sandbox-profiles.yaml")["assignments"]
    }

    evaluations = []
    for candidate in certification["candidates"]:
        pack_path = ROOT / candidate["pack_ref"]
        pack = yaml.safe_load(pack_path.read_text(encoding="utf-8"))
        validate(instance=pack, schema=PACK_SCHEMA)

        member_paths: list[Path] = []
        kinds: list[str] = []
        actual_profiles: set[str] = set()
        member_manifests_valid = True
        for member in pack["members"]:
            member_path = (pack_path.parent / member["manifest_ref"]).resolve()
            member_paths.append(member_path)
            payload = yaml.safe_load(member_path.read_text(encoding="utf-8"))
            validate(instance=payload, schema=MANIFEST_SCHEMA)
            kinds.append(payload["kind"])
            profile = sandbox_assignments.get(str(member_path))
            if profile is None:
                member_manifests_valid = False
            else:
                actual_profiles.add(profile)

        verdict = "pass"
        if candidate["target_level"] not in levels:
            verdict = "fail"
        if candidate["policy_bundle"] not in policy_bundles:
            verdict = "fail"
        if sorted(candidate["required_profiles"]) != sorted(actual_profiles):
            verdict = "fail"
        if not member_manifests_valid:
            verdict = "fail"

        evaluations.append(
            {
                "candidate_id": candidate["id"],
                "target_level": candidate["target_level"],
                "member_count": len(pack["members"]),
                "kinds": sorted(set(kinds)),
                "actual_profiles": sorted(actual_profiles),
                "policy_bundle": candidate["policy_bundle"],
                "public_track": candidate["public_track"],
                "signature": {
                    "profile": certification["signing_profile"]["id"],
                    "signer_role": certification["signing_profile"]["signer_role"],
                    "digest_sha256": digest_paths([pack_path, *member_paths]),
                },
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase18-extension-certification-report",
        "evaluations": evaluations,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in evaluations) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
