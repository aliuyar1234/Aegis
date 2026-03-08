#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/conformance-fixture-manifest.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/conformance-report.schema.json").read_text(encoding="utf-8")
)


def load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python scripts/run_contract_conformance.py <manifest.yaml> <report.yaml>")
        return 1

    manifest_path = ROOT / argv[1]
    report_path = ROOT / argv[2]
    manifest = load_yaml(manifest_path)
    report = load_yaml(report_path)
    validate(instance=manifest, schema=MANIFEST_SCHEMA)
    validate(instance=report, schema=REPORT_SCHEMA)

    transport = load_yaml(ROOT / "schema/transport-topology.yaml")
    subject_map = {subject["name"]: subject for subject in transport["subjects"]}
    manifest_messages = []

    for fixture in manifest["fixtures"]:
        subject = subject_map.get(fixture["subject_name"])
        if subject is None:
            raise SystemExit(f"Unknown transport subject in manifest: {fixture['subject_name']}")
        if subject["message"] != fixture["message_name"]:
            raise SystemExit(
                "Conformance fixture drift for "
                f"{fixture['id']}: topology={subject['message']} fixture={fixture['message_name']}"
            )
        manifest_messages.append(fixture["message_name"])

    covered = set(report["covered_messages"])
    if set(manifest_messages) != covered:
        raise SystemExit(
            "Conformance report message coverage drift: "
            f"manifest={sorted(set(manifest_messages))} report={sorted(covered)}"
        )

    print("Contract conformance assets validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
