PYTHON ?= python3
COMPOSE_FILE ?= infra/local/docker-compose.yml

.PHONY: bootstrap generate-docs validate validate-runtime validate-full ci validate-repo validate-schemas validate-traceability next-tasks phase-gates smoke local-up local-init local-down local-logs contracts-generate

bootstrap:
	bash scripts/bootstrap.sh

generate-docs:
	$(PYTHON) scripts/generate_docs.py

validate: generate-docs validate-repo validate-schemas validate-traceability phase-gates

validate-runtime:
	$(PYTHON) scripts/run_test_suites.py TS-003 TS-004 TS-005 TS-006 TS-007 TS-008 TS-009 TS-010 TS-011 TS-014 TS-015 TS-016 TS-017 TS-018

validate-full: validate validate-runtime

ci: validate-full

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
