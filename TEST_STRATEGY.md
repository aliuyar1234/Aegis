# TEST_STRATEGY.md

The canonical machine-readable test registry is `meta/test-suites.yaml`.

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

## Commands

See `meta/test-suites.yaml` for the authoritative commands and required paths.


## Phase-gate contract

Phase gates are defined by:
- `schema/jsonschema/phase-gate.schema.json`
- `tests/phase-gates/*.yaml`
- `scripts/run_phase_gate.py`

A phase gate is not just prose. It must reference fixtures, tests, acceptance criteria, and structured evidence for each step.
