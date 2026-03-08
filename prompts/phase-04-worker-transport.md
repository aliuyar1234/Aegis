# Prompt for PHASE-04

## Objective
Execute the next bounded implementation slice for PHASE-04 without reopening architecture decisions.

## Read first
- `docs/design-docs/transport-topology.md`
- `docs/design-docs/contracts-versioning.md`
- `schema/transport-topology.yaml`
- `schema/proto/README.md`

## Constraints
- Preserve the locked Aegis thesis.
- Do not bypass ADRs or invariants.
- Do not implement later-phase scope early.
- Update docs, task metadata, and generated artifacts when contracts or boundaries change.

## Tasks to complete
- `P04-T01`
- `P04-T02`
- `P04-T03`
- `P04-T04`

## Tests to run
- `TS-002`
- `TS-006`

## Acceptance criteria
- `AC-015`
- `AC-016`
- `AC-017`
- `AC-018`
- `AC-019`

## Required repo updates after coding
- Update task status in `work-items/task-index.yaml`.
- Regenerate docs with `python3 scripts/generate_docs.py`.
- Update tests, runbooks, and threat models when failure semantics changed.
