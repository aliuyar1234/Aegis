# architecture

Architecture tests validate invariants such as outbox-before-side-effects, no worker DB writes, and policy boundaries.

Every test suite in this directory should map back to `docs/overview/test-strategy.md` and the relevant acceptance criteria.
