# Prompt for PHASE-06

## Objective
Execute the next bounded implementation slice for PHASE-06 without reopening architecture decisions.

## Read first
- `docs/product-specs/operator-console.md`
- `docs/design-docs/projection-model.md`
- `schema/jsonschema/operator-session-view.schema.json`

## Constraints
- Preserve the locked Aegis thesis.
- Do not bypass ADRs or invariants.
- Do not implement later-phase scope early.
- Update docs, task metadata, and generated artifacts when contracts or boundaries change.

## Tasks to complete
- `P06-T01`
- `P06-T02`
- `P06-T03`
- `P06-T04`

## Tests to run
- `TS-008`

## Acceptance criteria
- `AC-024`
- `AC-025`
- `AC-026`
- `AC-027`

## Required repo updates after coding
- Update task status in `work-items/task-index.yaml`.
- Regenerate docs with `python3 scripts/generate_docs.py`.
- Update tests, runbooks, and threat models when failure semantics changed.
