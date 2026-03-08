#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/local/docker-compose.yml}"
MIGRATION_GLOB="${MIGRATION_GLOB:-apps/*/priv/postgres/migrations/*.sql}"

docker compose -f "$COMPOSE_FILE" up -d postgres nats minio jaeger otel-collector
# one-shot init containers

docker compose -f "$COMPOSE_FILE" up --wait nats-init minio-init || true

POSTGRES_CONTAINER_ID="$(docker compose -f "$COMPOSE_FILE" ps -q postgres)"

ensure_database() {
  local database="$1"

  docker exec "$POSTGRES_CONTAINER_ID" psql -U postgres -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$database'" | grep -q 1 || \
    docker exec "$POSTGRES_CONTAINER_ID" psql -U postgres -d postgres -c "CREATE DATABASE $database"
}

if [ -n "$POSTGRES_CONTAINER_ID" ]; then
  ensure_database "aegis_dev"
  ensure_database "aegis_test"

  while IFS= read -r migration_file; do
    [ -f "$migration_file" ] || continue
    docker exec -i "$POSTGRES_CONTAINER_ID" psql -U postgres -d aegis_dev < "$migration_file"
    docker exec -i "$POSTGRES_CONTAINER_ID" psql -U postgres -d aegis_test < "$migration_file"
  done < <(find apps -path "*/priv/postgres/migrations/*.sql" -print | awk -F/ '{print $NF "\t" $0}' | sort | cut -f2-)
fi

echo "Local stack initialized."
