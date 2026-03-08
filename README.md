# Aegis Runtime — Codex Handoff Repository v3

Aegis Runtime is a **BEAM-native durable runtime and control plane for long-lived AI sessions**. This repository is the implementation harness, architecture SSOT, task graph, validation surface, and anti-drift system for building it.

## Locked thesis

- Elixir/BEAM owns the control plane: session runtime, durability, orchestration, policy, approvals, replay, and operator console.
- Python owns execution-plane work: browser automation, model-heavy actions, provider integrations, and evals.
- Rust owns hot-path sidecars: media, protocol, recording, and performance-critical adapters.
- Browser-backed service operations is the first wedge.
- PostgreSQL is the canonical source of truth.
- Session timelines are append-only and event-sourced.
- Checkpoints plus event replay are mandatory.
- Exactly one authoritative live owner exists per session.
- Side effects launch only from committed intent via an outbox.
- NATS JetStream is the cross-language dispatch fabric, not the source of truth.
- Protobuf defines runtime contracts; JSON Schema defines tool I/O and operator-facing payloads.
- S3-compatible object storage stores artifacts.
- Operators and approvals are first-class runtime participants.

## Start here

1. `AGENTS.md`
2. `PRODUCT.md`
3. `ARCHITECTURE.md`
4. `meta/current-phase.yaml`
5. `IMPLEMENTATION_ORDER.md`
6. the phase doc named by `meta/current-phase.yaml`
7. `work-items/task-index.yaml`
8. `TEST_STRATEGY.md`
9. `ACCEPTANCE_CRITERIA.md`

## Current implementation state

- `PHASE-00` through `PHASE-13` are complete in this repository.
- `PHASE-13` remains the terminal current phase marker because there is no `PHASE-14`.
- `make next-tasks` should report that no unblocked tasks remain.

## What success looks like

Aegis is proving itself when it can:
1. create and own a session;
2. append events and checkpoints;
3. hydrate from checkpoint plus tail replay;
4. dispatch browser work through the execution bridge;
5. survive worker or node loss without silent duplicate side effects;
6. let an operator inspect, approve, intervene, and replay the session;
7. pass the internal and public phase gates under `tests/phase-gates/`.

## Repository map

See `REPO_MAP.md` for a navigable map and `NO_CONTEXT_SURVIVAL.md` for the no-context checklist.
