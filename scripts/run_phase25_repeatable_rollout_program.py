#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/repeatable-customer-rollout.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/repeatable-customer-rollout-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/repeatable-customer-rollout.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    track_ids = {item["id"] for item in load_yaml("meta/reference-deployment-tracks.yaml")["tracks"]}
    wave_ids = {item["id"] for item in load_yaml("meta/pilot-launch-wave.yaml")["waves"]}

    results = []
    for cohort in manifest["cohorts"]:
        verdict = "pass"
        if cohort["deployment_track"] not in track_ids:
            verdict = "fail"
        if cohort["predecessor_wave_id"] not in wave_ids:
            verdict = "fail"
        if not all((ROOT / rel).exists() for rel in cohort["required_inputs"] + cohort["handoff_doc_refs"] + cohort["runbook_refs"]):
            verdict = "fail"
        results.append(
            {
                "cohort_id": cohort["id"],
                "input_count": len(cohort["required_inputs"]),
                "handoff_count": len(cohort["handoff_doc_refs"]),
                "verdict": verdict,
            }
        )

    stages = {item["expansion_stage"] for item in manifest["cohorts"]}
    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and {"post_pilot_expansion", "ga_candidate"}.issubset(stages)

    report = {
        "id": "phase25-repeatable-customer-rollout-report",
        "cohorts": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
