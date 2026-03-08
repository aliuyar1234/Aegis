PYTHON ?= python
COMPOSE_FILE ?= infra/local/docker-compose.yml

.PHONY: bootstrap generate-docs validate validate-runtime validate-full ci validate-repo validate-schemas validate-traceability next-tasks phase-gates smoke local-up local-init local-down local-logs eval-up eval-init eval-down eval-logs eval-check eval-ready launch-check launch-ready prelaunch-check prelaunch-ready pilot-check pilot-ready ga-check ga-ready contracts-generate

bootstrap:
	$(PYTHON) scripts/bootstrap.py

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
	$(PYTHON) scripts/smoke.py

local-up:
	docker compose -f $(COMPOSE_FILE) up -d

local-init:
	$(PYTHON) scripts/init_local.py

local-down:
	docker compose -f $(COMPOSE_FILE) down

local-logs:
	docker compose -f $(COMPOSE_FILE) logs -f

eval-up: local-up

eval-init: local-init

eval-down: local-down

eval-logs: local-logs

eval-check:
	$(PYTHON) scripts/run_phase21_onboarding.py
	$(PYTHON) scripts/run_phase21_evaluation_deployment.py

eval-ready:
	$(MAKE) bootstrap
	$(MAKE) eval-up
	$(MAKE) eval-init
	$(MAKE) eval-check
	$(MAKE) smoke

launch-check:
	$(PYTHON) scripts/run_phase22_customer_golden_paths.py
	$(PYTHON) scripts/run_phase22_release_signoff.py
	$(PYTHON) scripts/run_phase22_security_baseline.py
	$(PYTHON) scripts/run_phase22_support_model.py
	$(PYTHON) scripts/build_phase22_launch_readiness_evidence.py --write docs/generated/phase-22-launch-readiness-evidence.json

launch-ready:
	$(MAKE) eval-ready
	$(MAKE) launch-check
	$(MAKE) validate

prelaunch-check:
	$(PYTHON) scripts/run_phase23_real_infrastructure_proving.py
	$(PYTHON) scripts/run_phase23_launch_observability.py
	$(PYTHON) scripts/run_phase23_customer_environment_readiness.py
	$(PYTHON) scripts/run_phase23_customer_operations_package.py
	$(PYTHON) scripts/run_phase23_pilot_governance.py
	$(PYTHON) scripts/build_phase23_launch_governance_evidence.py --write docs/generated/phase-23-launch-governance-evidence.json

prelaunch-ready:
	$(MAKE) launch-ready
	$(MAKE) prelaunch-check
	$(MAKE) validate

pilot-check:
	$(PYTHON) scripts/run_phase24_pilot_launch_wave.py
	$(PYTHON) scripts/run_phase24_pilot_control_room.py
	$(PYTHON) scripts/run_phase24_customer_feedback_loop.py
	$(PYTHON) scripts/run_phase24_launch_exception_governance.py
	$(PYTHON) scripts/run_phase24_pilot_exit_review.py
	$(PYTHON) scripts/build_phase24_pilot_operations_evidence.py --write docs/generated/phase-24-pilot-operations-evidence.json

pilot-ready:
	$(MAKE) prelaunch-ready
	$(MAKE) pilot-check
	$(MAKE) validate

ga-check:
	$(PYTHON) scripts/run_phase25_repeatable_rollout_program.py
	$(PYTHON) scripts/run_phase25_tenant_isolated_production_readiness.py
	$(PYTHON) scripts/run_phase25_service_scale_operations_readiness.py
	$(PYTHON) scripts/run_phase25_rollout_scorecards.py
	$(PYTHON) scripts/run_phase25_ga_transition_gate.py
	$(PYTHON) scripts/build_phase25_ga_transition_evidence.py --write docs/generated/phase-25-ga-transition-evidence.json

ga-ready:
	$(MAKE) pilot-ready
	$(MAKE) ga-check
	$(MAKE) validate
