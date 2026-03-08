#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def worker_crash_template(scenario_id: str, description: str) -> dict:
    return {
        "id": scenario_id,
        "version": 1,
        "seed": 14,
        "description": description,
        "steps": [
            {
                "id": "command-1",
                "kind": "command",
                "command": {
                    "action_id": f"{scenario_id}.action",
                    "worker_kind": "browser",
                    "effect": "read",
                },
            },
            {
                "id": "fault-1",
                "kind": "fault_injection",
                "fault": {
                    "fault_id": "worker_crash",
                    "target": "worker/browser-1",
                    "scope": "worker",
                    "expected_runtime_response": "resume_or_adopt_without_duplicate_effects",
                },
            },
            {
                "id": "artifact-1",
                "kind": "artifact_capture",
                "artifact": {
                    "kind": "evidence_note",
                    "label": f"{scenario_id}-evidence",
                },
            },
        ],
        "expected_terminal_state": {
            "session_state": "scaffolded",
            "recovery_status": "author_to_finalize",
            "uncertainty_status": "none",
            "quarantine_status": "clear",
            "replay_equivalent": True,
        },
        "proves": [
            "replace with the runtime property this scenario is intended to guard",
        ],
    }


def approval_timeout_template(scenario_id: str, description: str) -> dict:
    return {
        "id": scenario_id,
        "version": 1,
        "seed": 14,
        "description": description,
        "steps": [
            {
                "id": "command-1",
                "kind": "command",
                "command": {
                    "action_id": f"{scenario_id}.action",
                    "worker_kind": "browser",
                    "effect": "write",
                },
            },
            {
                "id": "approval-1",
                "kind": "approval",
                "approval": {
                    "action": "request",
                    "approval_id": f"{scenario_id}.approval",
                },
            },
            {
                "id": "approval-2",
                "kind": "approval",
                "approval": {
                    "action": "expire",
                    "approval_id": f"{scenario_id}.approval",
                },
            },
        ],
        "expected_terminal_state": {
            "session_state": "scaffolded",
            "recovery_status": "author_to_finalize",
            "uncertainty_status": "explicit_operator_absence",
            "quarantine_status": "clear",
            "replay_equivalent": True,
        },
        "proves": [
            "replace with the approval or timeout guarantee this scenario is intended to guard",
        ],
    }


TEMPLATES = {
    "worker_crash_recovery": worker_crash_template,
    "approval_timeout": approval_timeout_template,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", help="Path to the scenario YAML to create")
    parser.add_argument("--scenario-id", required=True, help="Stable scenario identifier")
    parser.add_argument(
        "--template",
        choices=sorted(TEMPLATES),
        default="worker_crash_recovery",
        help="Scaffold template",
    )
    parser.add_argument(
        "--description",
        help="Optional scenario description override",
    )
    args = parser.parse_args()

    description = args.description or (
        "Scaffolded deterministic simulation fixture. Customize steps, expected terminal state, "
        "and proves before registration."
    )
    payload = TEMPLATES[args.template](args.scenario_id, description)

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    try:
        rendered_path = output_path.relative_to(ROOT)
    except ValueError:
        rendered_path = output_path
    print(rendered_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
