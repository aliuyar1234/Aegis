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
MANIFEST_SCHEMA = json.loads((ROOT / "schema/jsonschema/phase24-pilot-operations-evidence-manifest.schema.json").read_text(encoding="utf-8"))
BUNDLE_SCHEMA = json.loads((ROOT / "schema/jsonschema/phase24-pilot-operations-evidence-bundle.schema.json").read_text(encoding="utf-8"))


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


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write")
    args = parser.parse_args(argv[1:])

    manifest = load_yaml("meta/phase24-pilot-operations-evidence-manifest.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    reports = [run_report(script_path) for script_path in manifest["required_scripts"]]
    if not all((ROOT / rel).exists() for rel in manifest["required_gates"]):
        raise SystemExit("PHASE-24 evidence manifest references missing gates.")
    for group in manifest["evidence_groups"]:
        if not all((ROOT / rel).exists() for rel in group["refs"]):
            raise SystemExit(f"PHASE-24 evidence group {group['id']} references missing assets.")

    bundle = {
        "id": manifest["bundle_id"],
        "phase": "PHASE-24",
        "reports": [{"id": report["id"], "verdict": report["verdict"]} for report in reports],
        "evidence_groups": [{"id": group["id"], "ref_count": len(group["refs"])} for group in manifest["evidence_groups"]],
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
