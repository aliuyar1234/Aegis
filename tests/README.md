# tests/

This directory is the blueprint for Aegis verification.

## Test doctrine

Prefer tests that prove:
- runtime truth
- recovery
- replay
- policy boundaries
- operator trust

over tests that merely increase line coverage.

## Subdirectories

- `contract/` — protobuf and schema contract tests
- `replay/` — checkpoint and replay tests
- `recovery/` — leases, adoption, and state recovery tests
- `chaos/` — failure injection
- `browser_e2e/` — browser wedge flows
- `architecture/` — invariant and boundary tests
- `smoke/` — quick repo/environment checks
- `phase-gates/` — demo acceptance scenarios
