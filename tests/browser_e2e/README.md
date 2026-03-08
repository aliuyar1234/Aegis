# browser_e2e

Browser E2E tests validate the first wedge: browser context lifecycle, artifacts, approvals, takeover, and uncertain side effects.

Phase 05 expectations:
- read-only fixtures validate artifact metadata and checkpoint-friendly browser handle recovery state
- effectful fixtures remain schema fixtures only and must be rejected by the Phase 05 browser worker
- uncertainty fixtures must declare operator takeover and trace evidence

Every test suite in this directory should map back to `TEST_STRATEGY.md` and the relevant acceptance criteria.
