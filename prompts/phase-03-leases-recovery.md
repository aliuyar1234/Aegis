# Prompt for PHASE-03

## Objective
Execute the next bounded implementation slice for PHASE-03 without reopening architecture decisions.

## Read first
- `docs/design-docs/runtime-model.md`
- `docs/operations/reliability.md`
- `docs/runbooks/node-loss.md`
- `docs/runbooks/lease-ambiguity.md`

## Constraints
- Preserve the locked Aegis thesis.
- Do not bypass ADRs or invariants.
- Do not implement later-phase scope early.
- Update docs, task metadata, and generated artifacts when contracts or boundaries change.

## Tasks to complete
- `P03-T01`
- `P03-T02`
- `P03-T03`
- `P03-T04`

## Tests to run
- `TS-005`
- `TS-010`

## Acceptance criteria
- `AC-012`
- `AC-013`
- `AC-014`

## Required repo updates after coding
- Update task status in `work-items/task-index.yaml`.
- Regenerate docs with `python3 scripts/generate_docs.py`.
- Update tests, runbooks, and threat models when failure semantics changed.
