# No-Context Survival

This repository is designed to survive a fresh Codex instance with zero external context.

## Checklist

A fresh Codex instance should be able to answer the following by reading the repo only:
- What Aegis is and is not (`docs/overview/product.md`)
- What the locked architecture is (`docs/overview/architecture.md` and `docs/design-docs/`)
- Which phase is current (`meta/current-phase.yaml`)
- What to build first (`docs/overview/implementation-order.md` and `make next-tasks`)
- What not to build first (`docs/overview/implementation-order.md` and phase docs)
- Which tasks are unblocked (`work-items/task-index.yaml`)
- Which tests define correctness (`docs/overview/test-strategy.md` and `meta/test-suites.yaml`)
- Which acceptance criteria define done (`docs/overview/acceptance-criteria.md` and `meta/acceptance-criteria.yaml`)
- Which invariants must never be violated (`docs/overview/must-not-violate.md` and `meta/invariants.yaml`)
- Which runbooks apply to named failure classes (`docs/runbooks/` and `meta/failure-runbooks.yaml`)

## Required starting sequence

1. Read `AGENTS.md`.
2. Read `docs/overview/product.md` and `docs/overview/architecture.md`.
3. Read `meta/current-phase.yaml`.
4. Read `docs/overview/implementation-order.md`.
5. Read the current phase doc.
6. Read `work-items/task-index.yaml`.
7. Run `make validate`.

If any answer requires chat history, the repository is wrong.
