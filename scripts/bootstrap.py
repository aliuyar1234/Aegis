#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def main() -> int:
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(VENV_DIR)

    python_bin = venv_python()
    subprocess.run([str(python_bin), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run(
        [str(python_bin), "-m", "pip", "install", "-r", str(ROOT / "requirements-dev.txt")],
        check=True,
    )

    print("Bootstrap complete.")
    print(f"Virtual environment: {VENV_DIR}")
    print(f"Use this interpreter for local runs: {python_bin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
