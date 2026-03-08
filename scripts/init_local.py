#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = os.environ.get("COMPOSE_FILE", "infra/local/docker-compose.yml")


def run(
    *args: str,
    check: bool = True,
    capture_output: bool = False,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=ROOT,
        check=check,
        capture_output=capture_output,
        text=True,
        input=input_text,
    )


def compose(
    *args: str, check: bool = True, capture_output: bool = False
) -> subprocess.CompletedProcess[str]:
    return run(
        "docker",
        "compose",
        "-f",
        COMPOSE_FILE,
        *args,
        check=check,
        capture_output=capture_output,
    )


def ensure_database(container_id: str, database: str) -> None:
    completed = run(
        "docker",
        "exec",
        container_id,
        "psql",
        "-U",
        "postgres",
        "-d",
        "postgres",
        "-tc",
        f"SELECT 1 FROM pg_database WHERE datname = '{database}'",
        capture_output=True,
    )
    if "1" not in completed.stdout:
        run(
            "docker",
            "exec",
            container_id,
            "psql",
            "-U",
            "postgres",
            "-d",
            "postgres",
            "-c",
            f"CREATE DATABASE {database}",
        )


def apply_migration(container_id: str, database: str, migration_file: Path) -> None:
    run(
        "docker",
        "exec",
        "-i",
        container_id,
        "psql",
        "-U",
        "postgres",
        "-d",
        database,
        input_text=migration_file.read_text(encoding="utf-8"),
    )


def main() -> int:
    compose("up", "-d", "postgres", "nats", "minio", "jaeger", "otel-collector")
    compose("up", "--wait", "nats-init", "minio-init", check=False)

    postgres_id = compose("ps", "-q", "postgres", capture_output=True).stdout.strip()
    if not postgres_id:
        print("Postgres container is not running.", file=sys.stderr)
        return 1

    ensure_database(postgres_id, "aegis_dev")
    ensure_database(postgres_id, "aegis_test")

    migrations = sorted(ROOT.glob("apps/*/priv/postgres/migrations/*.sql"), key=lambda path: path.name)
    for migration in migrations:
        apply_migration(postgres_id, "aegis_dev", migration)
        apply_migration(postgres_id, "aegis_test", migration)

    print("Local evaluation stack initialized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
