#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/policy-bundle-manifest.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/policy-bundle-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/policy-bundle-profiles.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    bundles = []
    for bundle in manifest["bundles"]:
        refs = [
            bundle["inputs"]["tool_registry_ref"],
            bundle["inputs"]["dangerous_actions_ref"],
            bundle["inputs"]["rbac_roles_ref"],
            bundle["inputs"]["abac_attributes_ref"],
            bundle["inputs"]["compatibility_policy_ref"],
            bundle["governance"]["rollback_runbook_ref"],
        ]
        verdict = "pass" if all((ROOT / ref).exists() for ref in refs) else "fail"
        bundles.append(
            {
                "bundle_id": bundle["id"],
                "explicit_input_count": len(bundle["inputs"]),
                "approval_role_count": len(bundle["governance"]["approval_roles"]),
                "explanation_field_count": len(bundle["governance"]["explanation_fields"]),
                "dual_control_required": bundle["governance"]["dual_control_required"],
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase18-policy-bundle-report",
        "bundles": bundles,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in bundles) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
