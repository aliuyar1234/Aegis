# aegis_runtime

## Purpose

Session kernel and supervisor logic

## Responsibilities

- authoritative session state
- lifecycle transitions
- command handling
- canonical per-session supervisor tree
- durable vs ephemeral state boundaries
- projection shaping over authoritative state
- lease-gated command acceptance and recovery flows

## Must not own

- hidden authoritative state outside the assigned boundary
- logic that belongs to another app just because it is convenient
- Postgres append/replay and outbox work
- lease ownership truth
- JetStream worker dispatch
- policy source-of-truth decisions
- operator projections as canonical state

## First implementation note

When adding code here, link the module or boundary to the relevant phase doc, ADR, acceptance criteria, and tests.

## Phase 01 modules

- `Aegis.Runtime` - public boundary API for session runtime work
- `Aegis.Runtime.SessionKernel` - authoritative state owner
- `Aegis.Runtime.SessionTreeSupervisor` - locked child tree using `:rest_for_one`
- `Aegis.Runtime.CommandHandler` - pure in-memory command/event pipeline
- `Aegis.Runtime.Projection` - stable operator-facing projection builder
- `Aegis.Runtime.OwnershipGuide` - module-level ownership map and golden example flow

## Phase 03 additions

- lease validation happens through `Aegis.Leases`, not caller-provided metadata
- `Aegis.Runtime.SessionKernel` now restores persisted sessions and exposes adoption/fencing APIs
- `apps/aegis_runtime/test/leases/lease_recovery_test.exs` covers stale epochs, self-fencing, and adoption
