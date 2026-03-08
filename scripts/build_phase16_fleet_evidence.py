#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/fleet-triage-manifest.schema.json").read_text(encoding="utf-8")
)
TRIAGE_REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/fleet-triage-report.schema.json").read_text(encoding="utf-8")
)
BUNDLE_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/operator-evidence-bundle.schema.json").read_text(encoding="utf-8")
)
REPORT_COMMANDS = [
    ["scripts/run_phase16_capacity.py"],
    ["scripts/run_phase16_placement.py"],
    ["scripts/run_phase16_overload.py"],
    ["scripts/run_phase16_isolation.py"],
    ["scripts/run_phase16_storage_scaling.py"],
]


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def run_report(command: list[str]) -> dict:
    completed = subprocess.run(
        [sys.executable, *command],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", help="Optional output path for the generated bundle")
    args = parser.parse_args(argv[1:])

    manifest = load_yaml("meta/fleet-triage-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)
    reports = [run_report(command) for command in REPORT_COMMANDS]
    report_index = {report["id"]: report for report in reports}

    cohort_results = []
    for cohort in manifest["cohorts"]:
        verdict = "pass" if all(report_index[ref]["verdict"] == "pass" for ref in cohort["report_refs"]) else "fail"
        cohort_results.append(
            {
                "cohort_id": cohort["id"],
                "report_count": len(cohort["report_refs"]),
                "runbook_count": len(cohort["runbook_refs"]),
                "evidence_fields": len(cohort["evidence_fields"]),
                "verdict": verdict,
            }
        )

    triage_report = {
        "id": "phase16-fleet-triage-report",
        "cohort_results": cohort_results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in cohort_results) else "fail",
    }
    validate(instance=triage_report, schema=TRIAGE_REPORT_SCHEMA)

    bundle = {
        "id": manifest["bundle_id"],
        "phase": "PHASE-16",
        "reports": [{"id": report["id"], "verdict": report["verdict"]} for report in reports],
        "cluster_summaries": triage_report["cohort_results"],
        "export_sections": manifest["export_sections"],
        "verdict": (
            "pass"
            if triage_report["verdict"] == "pass" and all(report["verdict"] == "pass" for report in reports)
            else "fail"
        ),
    }
    validate(instance=bundle, schema=BUNDLE_SCHEMA)

    rendered = json.dumps(bundle, indent=2, sort_keys=True)
    if args.write:
        output_path = ROOT / args.write
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"{rendered}\n", encoding="utf-8")

    print(rendered)
    return 0 if bundle["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
