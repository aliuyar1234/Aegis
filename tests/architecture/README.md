# architecture

Architecture tests validate invariants such as outbox-before-side-effects, no worker DB writes, and policy boundaries.

Every test suite in this directory should map back to `TEST_STRATEGY.md` and the relevant acceptance criteria.
