# Repository Map

## Overview docs

- `product.md` — locked project definition
- `architecture.md` — top-level architecture and system boundaries
- `implementation-order.md` — build order and defer order
- `acceptance-criteria.md` — objective done conditions by phase
- `test-strategy.md` — test suites, commands, and gate strategy
- `must-not-violate.md` — non-negotiable invariants under implementation pressure
- `can-change-later.md` — explicitly flexible areas
- `traceability-matrix.md` — how invariants map to ADRs, phases, tasks, tests, and runbooks
- `../project/patchlog-v2.md`, `../project/patchlog-v3.md`, and `../project/audit-remediation-matrix.md` — remediation history and audit fixes

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

- `../design-docs/runtime-model.md`
- `../design-docs/event-replay-model.md`
- `../design-docs/transport-topology.md`
- `../design-docs/contracts-versioning.md`
- `../design-docs/projection-model.md`
- `../design-docs/policy-decision-model.md`
- `../design-docs/browser-wedge.md`
- `../design-docs/security-governance.md`
- `../design-docs/multitenancy.md`
- `../design-docs/future-voice-media.md`

## Execution planning

- `../exec-plans/active/` — phase plans
- `../../work-items/task-index.yaml` — canonical task graph
- `../../work-items/phase-*.yaml` — generated phase task slices
- `../../prompts/` — bounded Codex operator prompts

## Contracts and schemas

- `../../schema/proto/` — runtime Protobuf contracts
- `../../schema/jsonschema/` — tool I/O, operator, artifact, and token schemas
- `../../schema/event-catalog/` — event registry and event-to-schema mapping
- `../../schema/event-payloads/` — typed payload schemas by event type
- `../../schema/checkpoints/` — checkpoint schema(s)
- `../../schema/transport-topology.yaml` — JetStream topology SSOT

## Tests and gates

- `../../test/` — ExUnit scaffolds for session/runtime concerns
- `../../tests/` — pytest scaffolds, fixtures, and phase gates
- `../../tests/phase-gates/*.yaml` — machine-checkable scenario gates
- `../../scripts/run_phase_gate.py` — gate validator/runner

## Infra and bootstrap

- `../../infra/local/` — local Docker Compose stack and init scripts
- `../../scripts/bootstrap.sh` — dev bootstrap
- `../../scripts/init_local.sh` — local stack initialization
- `../../scripts/validate_*.py` — repo, schema, and traceability validation
- `../../scripts/generate_docs.py` — generated artifact builder and freshness check
