# Prompt for PHASE-07

## Objective
Execute the next bounded implementation slice for PHASE-07 without reopening architecture decisions.

## Read first
- `docs/design-docs/policy-decision-model.md`
- `SECURITY.md`
- `schema/jsonschema/capability-token-claims.schema.json`
- `meta/dangerous-action-classes.yaml`

## Constraints
- Preserve the locked Aegis thesis.
- Do not bypass ADRs or invariants.
- Do not implement later-phase scope early.
- Update docs, task metadata, and generated artifacts when contracts or boundaries change.

## Tasks to complete
- `P07-T01`
- `P07-T02`
- `P07-T03`
- `P07-T04`

## Tests to run
- `TS-009`
- `TS-011`

## Acceptance criteria
- `AC-028`
- `AC-029`
- `AC-030`
- `AC-031`
- `AC-032`

## Required repo updates after coding
- Update task status in `work-items/task-index.yaml`.
- Regenerate docs with `python3 scripts/generate_docs.py`.
- Update tests, runbooks, and threat models when failure semantics changed.
