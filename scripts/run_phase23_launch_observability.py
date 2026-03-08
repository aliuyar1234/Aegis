#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/launch-observability-baseline.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/launch-observability-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/launch-observability-baseline.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    slo_ids = {item["id"] for item in load_yaml("meta/slo-profiles.yaml")["profiles"]}
    required_signals = {
        "session_ownership",
        "replay_health",
        "checkpoint_lag",
        "outbox_health",
        "worker_health",
        "artifact_upload_failures",
        "approval_backlog",
        "degraded_mode_entry",
    }

    covered = set()
    results = []
    for surface in manifest["surfaces"]:
        verdict = "pass"
        if surface["slo_profile_id"] not in slo_ids:
            verdict = "fail"
        if not all((ROOT / rel).exists() for rel in surface["doc_refs"] + surface["runbook_refs"]):
            verdict = "fail"
        covered.update(surface["signal_refs"])
        results.append(
            {
                "surface_id": surface["id"],
                "signal_count": len(surface["signal_refs"]),
                "verdict": verdict,
            }
        )

    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and required_signals.issubset(covered)

    report = {
        "id": "phase23-launch-observability-report",
        "surfaces": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
