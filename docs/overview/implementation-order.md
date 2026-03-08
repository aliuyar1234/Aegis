# Implementation Order

This document defines the build order, what to defer, and the first concrete success markers.

## Build order

1. PHASE-01 - Session kernel and state model
2. PHASE-02 - Event log, checkpoints, and replay
3. PHASE-03 - Lease ownership, fencing, and recovery
4. PHASE-04 - Worker contracts, transport, and execution bridge
5. PHASE-05 - Browser baseline: read-only flows, artifacts, resumable handles
6. PHASE-06 - Operator console and session inspection
7. PHASE-07 - Policy, approvals, capability tokens, dangerous-action defaults
8. PHASE-08 - Effectful browser flows, uncertainty, chaos, and demo gates
9. PHASE-09 - Multitenancy, quotas, authz, and audit
10. PHASE-10 - Extensibility surface and connector SDK
11. PHASE-11 - Voice/media expansion path
12. PHASE-12 - OSS core vs managed platform split
13. PHASE-13 - Cloud and enterprise hardening
14. PHASE-14 - Runtime conformance, deterministic simulation, and replay oracle
15. PHASE-15 - Upgrade safety, schema evolution, and disaster recovery
16. PHASE-16 - Fleet scheduling, isolation, and SLO-driven operability
17. PHASE-17 - Regional topology, fault domains, and session mobility
18. PHASE-18 - Certified ecosystem, governed extensions, and public compatibility leadership
19. PHASE-19 - Reference adoption, operator drills, and golden-path starter kits
20. PHASE-20 - Operational lifecycle governance, rollout waves, and deprecation discipline
21. PHASE-21 - Fresh-clone onboarding and official evaluation deployment
22. PHASE-22 - Customer golden paths, launch signoff, and support/security baseline
23. PHASE-23 - Operational proving, customer environment readiness, and pilot launch governance
24. PHASE-24 - Design-partner pilot execution, operating cadence, and exit review
25. PHASE-25 - GA transition, repeatable customer rollout, and service-scale readiness
26. PHASE-26 - Live customer operations, release automation, and field evidence governance

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
