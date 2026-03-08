# TECH_DEBT.md

Use this file to track deliberate compromises. Do not use it to hide architectural violations.

## Rules

- Every debt item must name the phase where it was introduced.
- Every debt item must describe the user/operator/runtime impact.
- Every debt item must identify the invariant it risks if left unresolved.
- Critical architectural debt must be linked to a task and phase exit criteria.

## Current seeded items

| Debt ID | Phase | Description | Risk if left unresolved |
|---|---|---|---|
| TD-001 | PHASE-00 | Local observability stack is scaffolding-only, not yet representative of full production telemetry. | Dev experience can mislead implementers about trace/debug expectations. |
| TD-002 | PHASE-05 | Initial browser workflows should stay narrow and controlled rather than pretending to cover arbitrary web automation. | Overclaiming wedge breadth can hide runtime weaknesses. |
| TD-003 | PHASE-11 | Voice/media path is intentionally deferred while preserving extension seams. | Premature voice work could destabilize the browser-first proof path. |
