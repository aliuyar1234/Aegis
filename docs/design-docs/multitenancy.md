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

## Isolation pitfalls to avoid

- cross-tenant artifact references
- shared secrets in worker environments
- unscoped traces and logs
- pooled browser contexts that can leak state
- policy engines that forget workspace-level context

## Interaction with phases

Phase 09 makes this real in implementation. Earlier phases must already carry the right identifiers so retrofitting is not required later.
