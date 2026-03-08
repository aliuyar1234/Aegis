# Multitenancy model

Aegis supports three isolation tiers without changing the core runtime semantics.

## Tier A — Shared plane
- shared control plane
- shared worker pools
- per-tenant quotas
- tenant/workspace scoping on every durable object

Use for early adopters, internal deployments, and lower-isolation customers.

## Tier B — Isolated execution
- shared control plane
- dedicated worker pools for one tenant
- dedicated artifact encryption key
- stronger routing and spend control
- routed worker subjects and pool IDs scoped per tenant

Use when execution isolation matters more than full control-plane isolation.

## Tier C — Dedicated deployment
- dedicated control plane
- dedicated worker pools
- dedicated secrets boundary
- tenant-specific deployment footprint

Use for highest-regulation or highest-trust tenants.

## Tenancy rules

- every event has `tenant_id` and `workspace_id`
- every action dispatch includes tenant/workspace identity
- every artifact ref is tenant-scoped
- every approval decision is tenant-scoped
- every operator request resolves tenant context before touching runtime APIs

## Quotas and admission control

Quota classes:
- live sessions
- concurrent browser contexts
- concurrent effectful actions
- artifact upload rate
- worker pool allocation
- operator subscription fan-out
- spend-bearing model usage (later)

Admission control is part of correctness, not only cost control.

Current implementation notes:
- live-session admission is enforced before the runtime starts a new session tree
- concurrent browser-context admission is enforced before bridge dispatch for browser work
- concurrent effectful-action admission is enforced before bridge dispatch for mutating work
- limits are selected by isolation tier, defaulting to Tier A until tier-aware routing metadata is fully represented durably
- quota checks are scoped by tenant and workspace so deferred dispatches can retry safely after capacity frees
- isolation tier is durable on session state and replay so worker routing does not depend on transient defaults
- Tier B and Tier C dispatch subjects derive tenant-scoped route keys, while worker registrations carry `worker_pool_id` and `isolation_tier` attributes

## Isolation pitfalls to avoid

- cross-tenant artifact references
- shared secrets in worker environments
- unscoped traces and logs
- pooled browser contexts that can leak state
- policy engines that forget workspace-level context

## Interaction with phases

Phase 09 makes this real in implementation. Earlier phases must already carry the right identifiers so retrofitting is not required later.
