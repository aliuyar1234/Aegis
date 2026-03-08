PYTHON ?= python3
COMPOSE_FILE ?= infra/local/docker-compose.yml

.PHONY: bootstrap generate-docs validate validate-repo validate-schemas validate-traceability next-tasks phase-gates smoke local-up local-init local-down local-logs contracts-generate

bootstrap:
	bash scripts/bootstrap.sh

generate-docs:
	$(PYTHON) scripts/generate_docs.py

validate: generate-docs validate-repo validate-schemas validate-traceability phase-gates

validate-repo:
	$(PYTHON) scripts/validate_repo.py

validate-schemas:
	$(PYTHON) scripts/validate_schemas.py

validate-traceability:
	$(PYTHON) scripts/validate_traceability.py

next-tasks:
	$(PYTHON) scripts/next_tasks.py

phase-gates:
	$(PYTHON) scripts/run_phase_gate.py tests/phase-gates/internal-demo.yaml tests/phase-gates/public-demo.yaml tests/phase-gates/enterprise-readiness.yaml tests/phase-gates/oss-managed-split.yaml tests/phase-gates/media-expansion.yaml

contracts-generate:
	bash scripts/generate_contracts.sh

smoke:
	bash scripts/smoke.sh

local-up:
	docker compose -f $(COMPOSE_FILE) up -d

local-init:
	bash scripts/init_local.sh

local-down:
	docker compose -f $(COMPOSE_FILE) down

local-logs:
	docker compose -f $(COMPOSE_FILE) logs -f
