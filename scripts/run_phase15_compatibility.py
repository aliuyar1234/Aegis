#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/compatibility-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def event_versions() -> list[str]:
    catalog = load_yaml(ROOT / "schema/event-catalog/events.yaml")
    versions = {f"v{item['version']}" for item in catalog["events"]}
    return sorted(versions)


def tool_versions() -> list[str]:
    registry = load_yaml(ROOT / "schema/tool-registry.yaml")
    return sorted({tool["version"] for tool in registry["tools"]})


def checkpoint_versions() -> list[str]:
    names = []
    for path in (ROOT / "schema/checkpoints").glob("*.schema.json"):
        stem = path.name.replace(".schema.json", "")
        names.append(stem)
    return sorted(names)


def observed_surface_versions() -> dict[str, list[str]]:
    extension_policy = load_yaml(ROOT / "meta/extension-compatibility-policy.yaml")
    return {
        "runtime-contract": sorted(extension_policy["aegis_runtime"]["supported_contract_versions"]),
        "session-checkpoint": checkpoint_versions(),
        "event-payload-catalog": event_versions(),
        "tool-registry": tool_versions(),
        "extension-api": sorted(extension_policy["extension_api"]["supported_versions"]),
    }


def main() -> int:
    matrix = load_yaml(ROOT / "meta/compatibility-matrix.yaml")
    skew_rules = load_yaml(ROOT / "meta/version-skew-rules.yaml")
    observed = observed_surface_versions()

    surface_results = []
    for surface in matrix["surfaces"]:
        surface_id = surface["id"]
        observed_versions = observed[surface_id]
        verdict = (
            "pass"
            if surface["current_version"] in surface["supported_versions"]
            and all(version in surface["supported_versions"] for version in observed_versions)
            else "fail"
        )
        surface_results.append(
            {
                "surface_id": surface_id,
                "observed_versions": observed_versions,
                "current_version": surface["current_version"],
                "supported_versions": surface["supported_versions"],
                "verdict": verdict,
            }
        )

    skew_rule_results = []
    for rule in skew_rules["rules"]:
        verdict = "pass" if rule["components"] and rule["deny_when"] else "fail"
        skew_rule_results.append(
            {
                "rule_id": rule["id"],
                "components": rule["components"],
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase15-compatibility-report",
        "surface_results": surface_results,
        "skew_rule_results": skew_rule_results,
        "verdict": (
            "pass"
            if all(item["verdict"] == "pass" for item in surface_results + skew_rule_results)
            else "fail"
        ),
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
