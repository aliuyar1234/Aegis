# Public mission-control demo

## Goal
Show approval-bound browser operations, explicit uncertainty, and operator intervention on one durable session timeline.

## Fixtures and evidence
- `tests/browser_e2e/fixtures/effectful_billing_address_update.yaml`
- `tests/browser_e2e/fixtures/effectful_entitlement_revoke.yaml`
- `tests/browser_e2e/fixtures/uncertain_submit_recovery.yaml`
- `docs/runbooks/browser-instability.md`
- `docs/runbooks/operator-intervention.md`

## Flow
1. Start the billing-address remediation flow and surface the live session in the operator console.
2. Show `approval.requested` and the exact action hash before the write dispatches.
3. Grant approval and confirm the browser submit path runs with capability-token scope and before/after artifacts.
4. Show a denied destructive fixture (`browser.delete`) to prove dangerous defaults still hold.
5. Trigger an uncertain browser mutation and confirm degraded mode plus operator takeover guidance instead of a silent retry.
6. Replay the session and show approvals, artifacts, failures, and operator actions on one timeline.

## Acceptance artifacts
- approval-bound write evidence with action hash
- capability-token-gated mutation path
- before/after browser artifacts and trace output
- denied destructive action evidence
- explicit uncertainty and operator takeover evidence
