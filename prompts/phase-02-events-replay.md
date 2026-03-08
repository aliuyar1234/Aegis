# Prompt for PHASE-02

## Objective
Execute the next bounded implementation slice for PHASE-02 without reopening architecture decisions.

## Read first
- `docs/design-docs/event-replay-model.md`
- `docs/design-docs/storage-model.md`
- `schema/event-catalog/events.yaml`
- `schema/checkpoints/session-checkpoint-v1.schema.json`

## Constraints
- Preserve the locked Aegis thesis.
- Do not bypass ADRs or invariants.
- Do not implement later-phase scope early.
- Update docs, task metadata, and generated artifacts when contracts or boundaries change.

## Tasks to complete
- `P02-T01`
- `P02-T02`
- `P02-T03`
- `P02-T04`

## Tests to run
- `TS-004`

## Acceptance criteria
- `AC-008`
- `AC-009`
- `AC-010`
- `AC-011`

## Required repo updates after coding
- Update task status in `work-items/task-index.yaml`.
- Regenerate docs with `python3 scripts/generate_docs.py`.
- Update tests, runbooks, and threat models when failure semantics changed.
