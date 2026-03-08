#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    {
        "cwd": ROOT,
        "command": f'"{sys.executable}" -m pytest tests/security -q',
    },
    {
        "cwd": ROOT / "apps" / "aegis_policy",
        "command": "mix test test/authorizer_test.exs",
    },
    {
        "cwd": ROOT / "apps" / "aegis_events",
        "command": "mix test test/replay/replay_test.exs",
    },
    {
        "cwd": ROOT / "apps" / "aegis_execution_bridge",
        "command": "mix test test/execution_bridge/execution_bridge_test.exs",
    },
    {
        "cwd": ROOT / "apps" / "aegis_execution_bridge",
        "command": "mix test test/execution_bridge/admission_control_test.exs",
    },
    {
        "cwd": ROOT / "apps" / "aegis_gateway",
        "command": "mix test test/operator_console/operator_console_authorization_test.exs",
    },
]


def main() -> int:
    for command in COMMANDS:
        completed = subprocess.run(command["command"], cwd=command["cwd"], shell=True)
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
