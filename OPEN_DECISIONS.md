# OPEN_DECISIONS.md

Architectural decisions are intentionally locked. This file only records **non-fatal tunables** that may change later without reopening the core thesis.

## OD-001 — Lease timing values
**Question:** Exact lease renewal interval, grace period, and adoption timeout.  
**Why open:** This affects operational tuning more than architecture.  
**Locked principle:** Postgres-backed single-owner leases with lease epochs and self-fencing.  
**Not allowed:** Replacing leases with cluster presence or eventual ownership.

## OD-002 — Initial browser backend packaging
**Question:** Pure Playwright worker versus abstraction layer that can later target external browser providers.  
**Recommendation:** Start with direct Playwright in Python but keep the control-plane browser handle contract provider-agnostic.  
**Locked principle:** Browser execution remains in Python; browser process state is never authoritative.

## OD-003 — Local observability stack shape
**Question:** Jaeger-only dev stack or a fuller LGTM-style dev stack later.  
**Why open:** This does not affect runtime semantics.  
**Locked principle:** Trace context must flow end to end and operators must have timeline-centric visibility regardless of backend choice.

No open decision in this file is allowed to violate `MUST_NOT_VIOLATE.md`.
