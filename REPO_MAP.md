# REPO_MAP.md

## Root SSOT docs

- `PRODUCT.md` — locked project definition
- `ARCHITECTURE.md` — top-level architecture and system boundaries
- `IMPLEMENTATION_ORDER.md` — build order and defer order
- `ACCEPTANCE_CRITERIA.md` — objective done conditions by phase
- `TEST_STRATEGY.md` — test suites, commands, and gate strategy
- `MUST_NOT_VIOLATE.md` — non-negotiable invariants under implementation pressure
- `CAN_CHANGE_LATER.md` — explicitly flexible areas
- `TRACEABILITY_MATRIX.md` — how invariants map to ADRs, phases, tasks, tests, and runbooks
- `PATCHLOG_V2.md`, `PATCHLOG_V3.md`, and `AUDIT_REMEDIATION_MATRIX.md` — remediation history and audit fixes

## Meta and machine-readable SSOT

- `meta/current-phase.yaml`
- `meta/invariants.yaml`
- `meta/phase-gates.yaml`
- `meta/acceptance-criteria.yaml`
- `meta/test-suites.yaml`
- `meta/generated-files.yaml`
- `meta/rbac-roles.yaml`
- `meta/abac-attributes.yaml`
- `meta/dangerous-action-classes.yaml`
- `meta/failure-runbooks.yaml`

## Deep technical docs

- `docs/design-docs/runtime-model.md`
- `docs/design-docs/event-replay-model.md`
- `docs/design-docs/transport-topology.md`
- `docs/design-docs/contracts-versioning.md`
- `docs/design-docs/projection-model.md`
- `docs/design-docs/policy-decision-model.md`
- `docs/design-docs/browser-wedge.md`
- `docs/design-docs/security-governance.md`
- `docs/design-docs/multitenancy.md`
- `docs/design-docs/future-voice-media.md`

## Execution planning

- `docs/exec-plans/active/` — phase plans
- `work-items/task-index.yaml` — canonical task graph
- `work-items/phase-*.yaml` — generated phase task slices
- `prompts/` — bounded Codex operator prompts

## Contracts and schemas

- `schema/proto/` — runtime Protobuf contracts
- `schema/jsonschema/` — tool I/O, operator, artifact, and token schemas
- `schema/event-catalog/` — event registry and event-to-schema mapping
- `schema/event-payloads/` — typed payload schemas by event type
- `schema/checkpoints/` — checkpoint schema(s)
- `schema/transport-topology.yaml` — JetStream topology SSOT

## Tests and gates

- `test/` — ExUnit scaffolds for session/runtime concerns
- `tests/` — pytest scaffolds, fixtures, and phase gates
- `tests/phase-gates/*.yaml` — machine-checkable scenario gates
- `scripts/run_phase_gate.py` — gate validator/runner

## Infra and bootstrap

- `infra/local/` — local Docker Compose stack and init scripts
- `scripts/bootstrap.sh` — dev bootstrap
- `scripts/init_local.sh` — local stack initialization
- `scripts/validate_*.py` — repo, schema, and traceability validation
- `scripts/generate_docs.py` — generated artifact builder and freshness check
