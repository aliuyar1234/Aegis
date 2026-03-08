#!/usr/bin/env bash
set -euo pipefail

python3 scripts/validate_repo.py
python3 scripts/validate_schemas.py
python3 scripts/validate_traceability.py
python3 scripts/run_phase_gate.py tests/phase-gates/internal-demo.yaml tests/phase-gates/public-demo.yaml tests/phase-gates/enterprise-readiness.yaml tests/phase-gates/oss-managed-split.yaml tests/phase-gates/media-expansion.yaml

if command -v docker >/dev/null 2>&1; then
  docker compose -f infra/local/docker-compose.yml config >/dev/null
else
  echo "docker not found; skipping compose config check."
fi

python3 scripts/next_tasks.py

echo "Smoke checks passed."
