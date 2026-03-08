#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/simulation-scenario.schema.json").read_text(encoding="utf-8")
)
RESULT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/simulation-result.schema.json").read_text(encoding="utf-8")
)

FAULT_EVENT_TYPES = {
    "worker_crash": "system.worker_crash_injected",
    "node_loss": "system.node_loss_injected",
    "approval_timeout": "approval.expired",
    "duplicate_callback": "action.duplicate_suppressed",
    "browser_instability": "action.browser_degraded",
}


def load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def scenario_event(step: dict) -> tuple[str, str]:
    kind = step["kind"]
    if kind == "command":
        return "action.requested", step["command"]["action_id"]
    if kind == "approval":
        action = step["approval"]["action"]
        if action == "request":
            return "approval.requested", step["approval"]["approval_id"]
        if action == "expire":
            return "approval.expired", step["approval"]["approval_id"]
        return f"approval.{action}ed", step["approval"]["approval_id"]
    if kind == "fault_injection":
        fault = step["fault"]
        return FAULT_EVENT_TYPES[fault["fault_id"]], fault["target"]
    if kind == "timer":
        return "timer.advanced", str(step["timer"]["advance_ms"])
    if kind == "artifact_capture":
        return "artifact.registered", step["artifact"]["label"]
    raise ValueError(f"Unsupported simulation step kind: {kind}")


def build_result(scenario: dict) -> dict:
    events = []
    faults_applied = []
    for seq_no, step in enumerate(scenario["steps"], start=1):
        event_type, detail = scenario_event(step)
        events.append(
            {
                "seq_no": seq_no,
                "step_id": step["id"],
                "event_type": event_type,
                "detail": detail,
            }
        )
        if step["kind"] == "fault_injection":
            faults_applied.append(step["fault"]["fault_id"])

    result = {
        "id": f"simulation-result-{scenario['id']}",
        "scenario_id": scenario["id"],
        "seed": scenario["seed"],
        "emitted_events": events,
        "faults_applied": faults_applied,
        "terminal_state": scenario["expected_terminal_state"],
        "invariants": scenario["proves"],
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result["result_signature"] = hashlib.sha256(canonical).hexdigest()
    validate(instance=result, schema=RESULT_SCHEMA)
    return result


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python scripts/run_simulation_scenario.py <scenario.yaml> [<scenario.yaml> ...]")
        return 1

    results = []
    for raw_path in argv[1:]:
        path = (ROOT / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path)
        scenario = load_yaml(path)
        validate(instance=scenario, schema=SCENARIO_SCHEMA)
        results.append(build_result(scenario))

    print(json.dumps(results if len(results) > 1 else results[0], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
