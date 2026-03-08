# Test Strategy

The canonical machine-readable test registry is `meta/test-suites.yaml`.
The registry-driven runner is `scripts/run_test_suites.py`.

## Principles

- Every critical path task links to tests and acceptance criteria.
- Replay, recovery, and policy are first-class test areas, not afterthoughts.
- Browser wedge tests include fixtures for read-only flows, mutation flows, and uncertainty scenarios.
- Phase gates are machine-checkable YAML scenarios, not prose-only checklists.
- Generated artifacts and cross-links are part of the validation surface.

## Test classes

- `TS-001` repo and anti-drift validation
- `TS-002` contracts, schemas, event payload coverage, transport topology
- `TS-003` session state model
- `TS-004` replay and checkpoint determinism
- `TS-005` lease ownership and recovery
- `TS-006` execution bridge and transport semantics
- `TS-007` browser wedge baseline and fixtures
- `TS-008` operator console and projection surfaces
- `TS-009` policy, approvals, and capability tokens
- `TS-010` recovery, uncertainty, and chaos
- `TS-011` security, multitenancy, and trust boundaries
- `TS-012` internal/public phase gates
- `TS-013` generated artifact freshness
- `TS-014` extensibility and connector compatibility
- `TS-015` voice/media boundary validation
- `TS-016` OSS/managed split gate
- `TS-017` enterprise readiness gate
- `TS-018` transport topology contract coverage
- `TS-019` replay oracle and determinism validation
- `TS-020` deterministic simulation validation
- `TS-021` contract conformance validation
- `TS-022` replay differential validation
- `TS-023` benchmark corpus and scorecard validation
- `TS-024` simulation fixture authoring-flow validation
- `TS-025` compatibility matrix and skew-policy validation
- `TS-026` upcaster manifest and migration-asset validation
- `TS-027` rolling-upgrade asset validation
- `TS-028` disaster-recovery and restore-objective validation
- `TS-029` standby-topology and promotion-surface validation
- `TS-030` release-evidence gate validation
- `TS-031` capacity-model and SLO-profile validation
- `TS-032` placement policy and pool-taxonomy validation
- `TS-033` load-shedding and overload-doctrine validation
- `TS-034` noisy-neighbor isolation validation
- `TS-035` storage-growth and transport-scaling validation
- `TS-036` fleet triage and operator-evidence validation
- `TS-037` regional topology and fault-domain validation
- `TS-038` region-aware placement validation
- `TS-039` regional evacuation and failover validation
- `TS-040` session mobility and continuity validation
- `TS-041` regional evidence-bundle validation
- `TS-042` extension certification validation
- `TS-043` sandbox-profile validation
- `TS-044` policy-bundle validation
- `TS-045` public compatibility-track validation
- `TS-046` ecosystem evidence-bundle validation
- `TS-047` adoption profile validation
- `TS-048` reference deployment-track validation
- `TS-049` operator exercise validation
- `TS-050` golden-path starter-kit validation
- `TS-051` adoption evidence-bundle validation
- `TS-052` operator accreditation validation
- `TS-053` rollout-wave validation
- `TS-054` incident-review packet validation
- `TS-055` deprecation governance validation
- `TS-056` lifecycle evidence-bundle validation

## Commands

See `meta/test-suites.yaml` for the authoritative commands and required paths.
Use `python3 scripts/run_test_suites.py TS-001 TS-003 ...` to execute suites directly from the registry without duplicating commands in CI or local tooling.


## Phase-gate contract

Phase gates are defined by:
- `schema/jsonschema/phase-gate.schema.json`
- `tests/phase-gates/*.yaml`
- `scripts/run_phase_gate.py`

A phase gate is not just prose. It must reference fixtures, tests, acceptance criteria, and structured evidence for each step.
