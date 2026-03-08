# Browser ops wedge product spec

## Wedge definition

The first wedge is browser-backed service operations in messy admin surfaces where reliability, artifacts, approvals, and human takeover matter.

## Phase split

### Baseline (PHASE-05)
- account lookup
- billing inspection
- entitlement inspection
- cross-tool investigation that stops before mutation

### Effectful (PHASE-08)
- billing address remediation
- entitlement revocation
- customer-state mutation with approval and before/after evidence

## Fixture source of truth

Example workflows are defined in:
- `tests/browser_e2e/fixtures/read_only_account_lookup.yaml`
- `tests/browser_e2e/fixtures/read_only_billing_inspection.yaml`
- `tests/browser_e2e/fixtures/effectful_billing_address_update.yaml`
- `tests/browser_e2e/fixtures/effectful_entitlement_revoke.yaml`
- `tests/browser_e2e/fixtures/uncertain_submit_recovery.yaml`

## Success criteria

The wedge is successful when the public demo feels like mission control, not a browser toy.
