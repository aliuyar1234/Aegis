# browser_e2e

Browser E2E tests validate the first wedge: browser context lifecycle, artifacts, approvals, takeover, and uncertain side effects.

Phase 08 expectations:
- read-only fixtures still validate artifact metadata and checkpoint-friendly browser handle recovery state
- approval-bound effectful fixtures execute only after explicit approval and capability-token checks
- effectful write fixtures capture before/after screenshots, DOM evidence, and trace output
- uncertainty fixtures surface an operator-takeover requirement instead of hiding write ambiguity

Every test suite in this directory should map back to `TEST_STRATEGY.md` and the relevant acceptance criteria.
