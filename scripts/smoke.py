#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run(list(args), cwd=ROOT, check=True)


def main() -> int:
    run(sys.executable, "scripts/validate_repo.py")
    run(sys.executable, "scripts/validate_schemas.py")
    run(sys.executable, "scripts/validate_traceability.py")
    run(
        sys.executable,
        "scripts/run_phase_gate.py",
        "tests/phase-gates/internal-demo.yaml",
        "tests/phase-gates/public-demo.yaml",
        "tests/phase-gates/enterprise-readiness.yaml",
        "tests/phase-gates/oss-managed-split.yaml",
        "tests/phase-gates/media-expansion.yaml",
    )

    if shutil.which("docker"):
        run("docker", "compose", "-f", "infra/local/docker-compose.yml", "config")
    else:
        print("docker not found; skipping compose config check.")

    run(sys.executable, "scripts/next_tasks.py")
    print("Smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
