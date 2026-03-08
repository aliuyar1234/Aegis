#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/replay-fixture-manifest.schema.json").read_text(encoding="utf-8")
)
RESULT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/replay-diff-result.schema.json").read_text(encoding="utf-8")
)


def load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def run_scenario(path: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "scripts/run_simulation_scenario.py", path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def terminal_state_equal(left: dict, right: dict) -> bool:
    return left == right


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scripts/run_replay_diff.py <manifest.yaml>")
        return 1

    manifest = load_yaml(ROOT / argv[1])
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    fixture_results = []
    for fixture in manifest["fixtures"]:
        current = run_scenario(fixture["scenario_ref"])
        current_signature_match = current["result_signature"] == fixture["current_baseline"]["result_signature"]
        current_event_types = [item["event_type"] for item in current["emitted_events"]]
        previous_supported_equivalent = (
            current_event_types == fixture["previous_supported_baseline"]["event_types"]
            and terminal_state_equal(current["terminal_state"], fixture["previous_supported_baseline"]["terminal_state"])
            and current["terminal_state"]["replay_equivalent"] is True
        )
        verdict = "pass" if current_signature_match and previous_supported_equivalent else "fail"
        fixture_results.append(
            {
                "fixture_id": fixture["id"],
                "comparison_mode": fixture["comparison_mode"],
                "current_signature_match": current_signature_match,
                "previous_supported_equivalent": previous_supported_equivalent,
                "verdict": verdict,
            }
        )

    report = {
        "id": "replay-diff-report",
        "fixture_results": fixture_results,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in fixture_results) else "fail",
    }
    validate(instance=report, schema=RESULT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
