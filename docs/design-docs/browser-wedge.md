# Browser wedge architecture

Browser-backed service operations is the first proof surface for Aegis.

## Split the wedge correctly

### PHASE-05: browser baseline
Read-only flows only:
- open context
- navigate
- inspect visible state
- capture artifacts
- verify expected state
- persist resumable handle metadata

No effectful writes are allowed in PHASE-05.

### PHASE-08: effectful browser flows
Effectful writes only after:
- tool descriptor validation
- policy evaluation
- approval binding
- capability token issuance
- before/after artifact requirements
- uncertainty handling

## Artifact requirements

Every browser scenario must define expected artifacts in fixture form.
Read-only baseline artifact kinds:
- screenshot
- dom_snapshot

Required artifact kinds for effectful writes:
- pre-write screenshot
- post-write screenshot
- stable DOM snapshot or equivalent evidence
- trace when uncertainty or failure occurs

## Recovery rules

- read-only baseline recovery may reattach or restart without human approval
- read-only handles must retain a stable-page marker, last stable artifact id, and restart hint
- effectful browser writes move to uncertainty if side-effect certainty is lost
- operator takeover is a mode change, not a side channel

## Fixture source of truth

Browser wedge fixtures live in `tests/browser_e2e/fixtures/` and validate against `schema/jsonschema/browser-workflow-fixture.schema.json`.

## Mutation taxonomy

- `read_only` means inspect, extract, verify, and capture evidence only
- `browser_write_medium` means a user-visible mutation that normally requires approval
- `browser_write_high` means an effectful or destructive mutation that requires approval

## Fixture contract

Every fixture must declare:
- `mutation_class`
- `requires_approval`
- `expected_policy_decision`
- `expected_artifacts`
- `requires_operator_takeover_on_uncertainty`

Phase 05 workers may execute only `read_only` fixtures. They must reject mutating steps such as `click`, `fill`, and `submit` even if those step kinds are allowed by the shared schema for later phases.
