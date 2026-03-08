#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/rollout-scorecard-program.schema.json").read_text(encoding="utf-8"))
REPORT_SCHEMA = json.loads((ROOT / "schema/jsonschema/rollout-scorecard-report.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/rollout-scorecard-program.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    results = []
    for scorecard in manifest["scorecards"]:
        verdict = "pass"
        if not all((ROOT / rel).exists() for rel in scorecard["evidence_refs"] + scorecard["doc_refs"] + scorecard["runbook_refs"]):
            verdict = "fail"
        if len(scorecard["metrics"]) < 3:
            verdict = "fail"
        results.append(
            {
                "scorecard_id": scorecard["id"],
                "metric_count": len(scorecard["metrics"]),
                "evidence_count": len(scorecard["evidence_refs"]),
                "verdict": verdict,
            }
        )

    stages = {item["stage"] for item in manifest["scorecards"]}
    overall = all(item["verdict"] == "pass" for item in results)
    overall = overall and {"post_pilot_expansion", "ga_transition"}.issubset(stages)

    report = {
        "id": "phase25-rollout-scorecard-report",
        "scorecards": results,
        "verdict": "pass" if overall else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
