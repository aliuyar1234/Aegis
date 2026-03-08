#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/incident-review-packets.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/incident-review-packet-report.schema.json").read_text(
        encoding="utf-8"
    )
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> int:
    manifest = load_yaml("meta/incident-review-packets.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    exercises = {
        item["id"] for item in load_yaml("meta/operator-exercise-manifest.yaml")["exercises"]
    }
    accreditation = {
        item["id"]: item for item in load_yaml("meta/operator-accreditation.yaml")["tracks"]
    }

    results = []
    for packet in manifest["packets"]:
        verdict = "pass"
        accreditation_track = accreditation.get(packet["accreditation_track"])
        if packet["source_exercise"] not in exercises:
            verdict = "fail"
        if accreditation_track is None:
            verdict = "fail"
        elif packet["source_exercise"] not in accreditation_track["required_exercises"]:
            verdict = "fail"
        if not all(path_exists(ref) for ref in packet["required_evidence"]):
            verdict = "fail"
        if not all(path_exists(ref) for ref in packet["runbook_refs"]):
            verdict = "fail"
        if not all(path_exists(ref) for ref in packet["follow_up_refs"]):
            verdict = "fail"

        results.append(
            {
                "packet_id": packet["id"],
                "runbook_count": len(packet["runbook_refs"]),
                "evidence_count": len(packet["required_evidence"]),
                "follow_up_count": len(packet["follow_up_refs"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase20-incident-review-packet-report",
        "packets": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
