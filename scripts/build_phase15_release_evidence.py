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
    (ROOT / "schema/jsonschema/release-evidence-manifest.schema.json").read_text(encoding="utf-8")
)
BUNDLE_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/release-evidence-bundle.schema.json").read_text(encoding="utf-8")
)

REPORT_COMMANDS = [
    ["scripts/run_phase15_compatibility.py"],
    ["scripts/run_upcaster_coverage.py"],
    ["scripts/run_upgrade_drill.py"],
    ["scripts/run_restore_drill.py"],
    ["scripts/run_standby_promotion.py"],
]


def load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


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

    manifest = load_yaml(ROOT / "meta/release-evidence-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)
    reports = [run_report(command) for command in REPORT_COMMANDS]
    bundle = {
        "id": "phase15-release-evidence-bundle",
        "candidate": manifest["candidate"],
        "reports": [{"id": report["id"], "verdict": report["verdict"]} for report in reports],
        "required_gates": manifest["required_gates"],
        "verdict": "pass" if all(report["verdict"] == "pass" for report in reports) else "fail",
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
