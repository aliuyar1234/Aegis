# Implementation Order

This document defines the build order, what to defer, and the first concrete success markers.

## Build order

1. PHASE-01 — Session kernel and state model
2. PHASE-02 — Event log, checkpoints, and replay
3. PHASE-03 — Lease ownership, fencing, and recovery
4. PHASE-04 — Worker contracts, transport, and execution bridge
5. PHASE-05 — Browser baseline: read-only flows, artifacts, resumable handles
6. PHASE-06 — Operator console and session inspection
7. PHASE-07 — Policy, approvals, capability tokens, dangerous-action defaults
8. PHASE-08 — Effectful browser flows, uncertainty, chaos, and demo gates
9. PHASE-09 — Multitenancy, quotas, authz, and audit
10. PHASE-10 — Extensibility surface and connector SDK
11. PHASE-11 — Voice/media expansion path
12. PHASE-12 — OSS core vs managed platform split
13. PHASE-13 — Cloud and enterprise hardening

## What not to build first

Do not start with:
- a generic workflow builder
- broad multi-agent orchestration
- customer-facing product polish
- voice/media
- marketplace ideas
- custom model hosting
- enterprise packaging
- analytics warehouse work
- multi-region active/active

## First 2 weeks

Success in the first 2 weeks means:
- repo validation and generated artifact freshness are clean;
- local stack boots and initializes without hidden manual steps;
- SessionKernel skeleton exists;
- event, checkpoint, and projection contracts are stable enough to start coding;
- a fresh Codex instance can identify the next five tasks without human explanation.

Focus: PHASE-01, early PHASE-02, and validator discipline.

## First 8 weeks

Success in the first 8 weeks means:
- sessions can be created, owned, checkpointed, and replayed;
- events append atomically with outbox;
- JetStream dispatch and worker lifecycle exist;
- browser workers capture artifacts;
- operator console can inspect and replay sessions;
- approval model exists;
- internal demo gate passes.

Focus: PHASE-01 through PHASE-08.

## First internal demo

The internal demo is defined by `tests/phase-gates/internal-demo.yaml`.
It proves runtime credibility: create session, capture browser artifacts, crash worker or SessionKernel, recover via checkpoint plus replay, continue safely, and replay the session.

## First public demo

The public demo is defined by `tests/phase-gates/public-demo.yaml`.
It proves mission-control credibility: live browser service operation, approval-bound write, failure, recovery, operator intervention, and historical replay.

## Irreversible decisions to respect

- session-first runtime model
- single-owner semantics
- Postgres as truth
- event-sourced session timeline
- structured checkpoints plus replay
- outbox before side effects
- JetStream as transport, not truth
- Protobuf + JSON Schema contracts
- browser-first wedge
- sidecars over NIFs

See `docs/adr/`.
