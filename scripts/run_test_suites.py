#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "meta" / "test-suites.yaml"


def load_registry() -> dict[str, dict]:
    payload = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    suites = payload.get("test_suites", [])
    return {suite["id"]: suite for suite in suites}


def normalize_command(command: str) -> str:
    stripped = command.lstrip()

    if stripped.startswith("python3 "):
        return f'"{sys.executable}" {stripped[len("python3 "):]}'

    if stripped.startswith("python "):
        return f'"{sys.executable}" {stripped[len("python "):]}'

    if stripped.startswith("pytest "):
        return f'"{sys.executable}" -m {stripped}'

    return command


def run_suite(suite: dict) -> int:
    suite_id = suite["id"]
    title = suite.get("title", suite_id)
    command = normalize_command(suite["command"])

    print(f"==> {suite_id}: {title}", flush=True)
    print(f"    {command}", flush=True)
    completed = subprocess.run(command, cwd=ROOT, shell=True)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run test suites from meta/test-suites.yaml")
    parser.add_argument("suite_ids", nargs="*", help="One or more suite IDs, for example TS-001 TS-003")
    parser.add_argument("--list", action="store_true", help="List known suite IDs and exit")
    args = parser.parse_args()

    registry = load_registry()

    if args.list:
        for suite_id in sorted(registry):
            suite = registry[suite_id]
            print(f"{suite_id}: {suite.get('title', suite_id)}")
        return 0

    if not args.suite_ids:
        parser.error("at least one suite ID is required unless --list is used")

    unknown = [suite_id for suite_id in args.suite_ids if suite_id not in registry]
    if unknown:
        print(f"Unknown suite IDs: {', '.join(unknown)}", file=sys.stderr)
        print(f"Known suite IDs: {', '.join(sorted(registry))}", file=sys.stderr)
        return 1

    for suite_id in args.suite_ids:
        result = run_suite(registry[suite_id])
        if result != 0:
            return result

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
