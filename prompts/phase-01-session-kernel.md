# Prompt for PHASE-01

## Objective
Execute the next bounded implementation slice for PHASE-01 without reopening architecture decisions.

## Read first
- `AGENTS.md`
- `docs/overview/product.md`
- `docs/overview/architecture.md`
- `docs/design-docs/runtime-model.md`
- `meta/current-phase.yaml`

## Constraints
- Preserve the locked Aegis thesis.
- Do not bypass ADRs or invariants.
- Do not implement later-phase scope early.
- Update docs, task metadata, and generated artifacts when contracts or boundaries change.

## Tasks to complete
- `P01-T01`
- `P01-T02`
- `P01-T03`
- `P01-T04`

## Tests to run
- `TS-003`

## Acceptance criteria
- `AC-005`
- `AC-006`
- `AC-007`

## Required repo updates after coding
- Update task status in `work-items/task-index.yaml`.
- Regenerate docs with `python3 scripts/generate_docs.py`.
- Update tests, runbooks, and threat models when failure semantics changed.
