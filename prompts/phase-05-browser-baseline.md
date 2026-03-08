# Prompt for PHASE-05

## Objective
Execute the next bounded implementation slice for PHASE-05 without reopening architecture decisions.

## Read first
- `docs/design-docs/browser-wedge.md`
- `docs/product-specs/browser-ops-wedge.md`
- `tests/browser_e2e/fixtures/read_only_account_lookup.yaml`

## Constraints
- Preserve the locked Aegis thesis.
- Do not bypass ADRs or invariants.
- Do not implement later-phase scope early.
- Update docs, task metadata, and generated artifacts when contracts or boundaries change.

## Tasks to complete
- `P05-T01`
- `P05-T02`
- `P05-T03`
- `P05-T04`

## Tests to run
- `TS-007`

## Acceptance criteria
- `AC-020`
- `AC-021`
- `AC-022`
- `AC-023`

## Required repo updates after coding
- Update task status in `work-items/task-index.yaml`.
- Regenerate docs with `python3 scripts/generate_docs.py`.
- Update tests, runbooks, and threat models when failure semantics changed.
