#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SUITES = {
    "TS-003": {
        "cwd": ROOT / "apps" / "aegis_runtime",
        "command": "mix test test/session_state",
    },
    "TS-004": {
        "cwd": ROOT / "apps" / "aegis_events",
        "command": "mix test test/replay",
    },
    "TS-005": {
        "cwd": ROOT / "apps" / "aegis_runtime",
        "command": "mix test test/leases",
    },
    "TS-006": {
        "cwd": ROOT / "apps" / "aegis_execution_bridge",
        "command": "mix test test/execution_bridge",
    },
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in SUITES:
        print(f"Usage: {Path(sys.argv[0]).name} <{'|'.join(SUITES)}>")
        return 1

    suite = SUITES[sys.argv[1]]
    completed = subprocess.run(suite["command"], cwd=suite["cwd"], shell=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
