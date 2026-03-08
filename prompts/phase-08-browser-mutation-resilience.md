# Prompt for PHASE-08

## Objective
Execute the next bounded implementation slice for PHASE-08 without reopening architecture decisions.

## Read first
- `docs/design-docs/browser-wedge.md`
- `RELIABILITY.md`
- `tests/browser_e2e/fixtures/effectful_billing_address_update.yaml`
- `tests/phase-gates/internal-demo.yaml`

## Constraints
- Preserve the locked Aegis thesis.
- Do not bypass ADRs or invariants.
- Do not implement later-phase scope early.
- Update docs, task metadata, and generated artifacts when contracts or boundaries change.

## Tasks to complete
- `P08-T06`
- `P08-T01`
- `P08-T02`
- `P08-T04`

## Tests to run
- `TS-007`
- `TS-009`
- `TS-010`
- `TS-012`

## Acceptance criteria
- `AC-033`
- `AC-034`
- `AC-035`
- `AC-036`
- `AC-037`

## Required repo updates after coding
- Update task status in `work-items/task-index.yaml`.
- Regenerate docs with `python3 scripts/generate_docs.py`.
- Update tests, runbooks, and threat models when failure semantics changed.
