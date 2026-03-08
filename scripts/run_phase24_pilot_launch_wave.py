#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/pilot-launch-wave.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/pilot-launch-wave-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/pilot-launch-wave.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    track_ids = {item["id"] for item in load_yaml("meta/reference-deployment-tracks.yaml")["tracks"]}
    golden_path_ids = {item["id"] for item in load_yaml("meta/customer-golden-paths.yaml")["paths"]}

    results = []
    for wave in manifest["waves"]:
        verdict = "pass"
        if wave["deployment_track"] not in track_ids:
            verdict = "fail"
        if wave["golden_path_id"] not in golden_path_ids:
            verdict = "fail"
        if not (ROOT / wave["go_no_go_bundle"]).exists():
            verdict = "fail"
        if not all((ROOT / rel).exists() for rel in wave["communication_refs"] + wave["runbook_refs"]):
            verdict = "fail"
        results.append(
            {
                "wave_id": wave["id"],
                "communication_count": len(wave["communication_refs"]),
                "verdict": verdict,
            }
        )

    report = {
        "id": "phase24-pilot-launch-wave-report",
        "waves": results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in results) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
