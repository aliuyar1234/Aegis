# Roadmap

## Planning horizon

This roadmap assumes a strong team, no pressure to optimize for the easiest MVP, and a mandate to build the right system.

## v1 — Runtime credibility

**Goal:** prove the runtime thesis through the browser-ops wedge.

### Must exist
- SessionKernel and lifecycle
- Postgres event log + checkpoints + replay
- lease ownership and adoption
- JetStream execution bridge
- browser worker with artifacts
- operator console
- policy and approvals
- recovery hardening for worker/node/browser failures
- internal and public demo scenarios

### Proof points
- session survives partial failure
- browser work is controllable and replayable
- humans can inspect and intervene
- approvals and uncertain side effects are explicit
- architecture feels like a control plane, not a chatbot

## v2 — Platformization

**Goal:** move from strong wedge implementation to reusable platform.

### Must exist
- stable connector/extension surface
- stronger multitenancy isolation and quotas
- richer policy model
- better search and observability
- managed execution pools
- packaging for self-hosted vs managed deployments
- clearer OSS-core / platform boundary

### Proof points
- new connectors can be added without hidden architecture knowledge
- tenant isolation is practical, not theoretical
- platform adoption no longer depends on the original authors

## v3 — Strategic category play

**Goal:** turn Aegis into a broader durable AI operations platform.

### Candidate expansions
- voice/media pack
- simulation/evaluation pack
- dedicated enterprise deployments
- managed cloud control plane
- ecosystem around runtime and connectors

### Proof points
- Aegis is recognized as infrastructure, not only a wedge app
- the runtime core attracts serious extension work
- product moat shifts from demos to operational trust and reliability

## Success milestones

### First 2 weeks
- repo harness locked
- phase/task/test/acceptance system working
- local stack boots
- SessionKernel skeleton begun
- no-context survival validated

### First 8 weeks
- session + events + replay + leases + execution bridge + browser wedge skeleton
- internal demo runs end to end
- operator console exists in usable form
- phase-gate tests start becoming real rather than aspirational

### Beyond 8 weeks
- reliability hardening
- multitenancy and quotas
- public demo readiness
- connector and platformization work

## What roadmap does not mean

This roadmap is **not** license to parallelize everything. The implementation order remains governed by `../overview/implementation-order.md` and the phase docs.

## Post-PHASE-13 extension

PHASE-26 is now the latest committed continuation of the original roadmap.
It moves beyond repo-level GA transition proof into the post-GA operating problem:
live customer operations, release automation, field evidence capture, and lifecycle
governance that can hold once Aegis is running for real customers.

For the broader successor arc beyond the original PHASE-00 through PHASE-13 plan,
see [State-of-the-art roadmap extension](state-of-the-art-roadmap.md).
