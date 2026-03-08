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
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/launch-readiness-evidence-manifest.schema.json").read_text(encoding="utf-8"))
BUNDLE_SCHEMA = json.loads((ROOT / "schema/jsonschema/launch-readiness-evidence-bundle.schema.json").read_text(encoding="utf-8"))


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def run_report(script_path: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, script_path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()

    manifest = load_yaml("meta/launch-readiness-evidence-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    reports = [run_report(script_path) for script_path in manifest["required_scripts"]]
    if not all((ROOT / rel).exists() for rel in manifest["required_gates"] + manifest["required_docs"]):
        raise SystemExit("Launch readiness evidence manifest references missing docs or gates.")

    bundle = {
        "id": "phase22-launch-readiness-evidence-bundle",
        "phase": "PHASE-22",
        "reports": [
            {"report_id": report["id"], "verdict": report["verdict"]}
            for report in reports
        ],
        "verdict": "pass" if all(report["verdict"] == "pass" for report in reports) else "fail",
    }
    validate(instance=bundle, schema=BUNDLE_SCHEMA)

    payload = json.dumps(bundle, indent=2, sort_keys=True)
    if args.write:
        args.write.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if bundle["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
