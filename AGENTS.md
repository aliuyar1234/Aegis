# AGENTS.md

This repository is the **single source of truth** for implementing **Aegis Runtime**. Do not rely on chat history.

## Read order

1. `README.md`
2. `docs/overview/product.md`
3. `docs/overview/architecture.md`
4. `meta/current-phase.yaml`
5. `docs/overview/implementation-order.md`
6. the current phase doc listed in `meta/current-phase.yaml`
7. `work-items/task-index.yaml`
8. `docs/overview/test-strategy.md`
9. `docs/overview/must-not-violate.md`

## What Aegis is

Aegis Runtime is a **BEAM-native durable control plane for long-lived AI sessions**.
- Elixir owns session runtime, durability, orchestration, policy, approvals, replay, and operator console.
- Python owns execution-plane work such as browser automation, model-heavy actions, and provider integrations.
- Rust owns hot-path sidecars for media, protocol, recording, and performance-sensitive adapters.

## Non-negotiables

- Session is the primary abstraction.
- Exactly one authoritative live owner exists per session.
- PostgreSQL is the source of truth.
- Session timelines are append-only and event-sourced.
- Checkpoints plus replay are mandatory.
- Side effects launch only from committed intent via an outbox.
- NATS JetStream is transport, not truth.
- Workers never own authoritative state.
- Operators and approvals are first-class runtime participants.
- Browser-backed service operations is the first wedge.

See `docs/overview/must-not-violate.md` and `meta/invariants.yaml`.

## How to work

- Start from the **current phase** in `meta/current-phase.yaml`.
- Pick bounded work from `work-items/task-index.yaml` or `make next-tasks`.
- Read the linked ADRs, acceptance criteria, and tests before coding.
- Do not implement later-phase scope early.
- Update docs, tasks, schemas, and generated artifacts when architecture changes.
- Run `make validate` before considering work complete.

## Where truth lives

- Project definition: `docs/overview/product.md`
- Architecture: `docs/overview/architecture.md` and `docs/design-docs/`
- Phase plans: `docs/exec-plans/active/`
- Tasks: `work-items/`
- Contracts and schemas: `schema/`
- Tests and gates: `tests/` and `docs/overview/test-strategy.md`
- Invariants and traceability: `meta/` and `docs/overview/traceability-matrix.md`
- Runbooks: `docs/runbooks/`
- Irreversible decisions: `docs/adr/`

## Never do these things

- Do not make Elixir a thin wrapper around Python.
- Do not let workers write canonical runtime tables.
- Do not dispatch side effects before commit/outbox.
- Do not bypass policy/approval boundaries.
- Do not treat JetStream as the source of truth.
- Do not add a generic workflow builder before the runtime is proven.
- Do not put large blobs on the control-plane event stream.

## Useful commands

- `make bootstrap`
- `make eval-up`
- `make eval-init`
- `make eval-check`
- `make eval-ready`
- `make launch-check`
- `make launch-ready`
- `make prelaunch-check`
- `make prelaunch-ready`
- `make pilot-check`
- `make pilot-ready`
- `make ga-check`
- `make ga-ready`
- `make validate`
- `make next-tasks`
- `make generate-docs`
- `make phase-gates`
- `make local-up`
- `make local-init`
- `make smoke`
