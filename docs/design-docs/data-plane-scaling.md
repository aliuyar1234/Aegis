# Data-plane scaling plan

## Purpose

PHASE-16 formalizes scaling plans for the truth store, outbox, projections, and
artifact indexes. This is a planning and evidence surface, not a license to replace
the core architecture.

## Non-negotiables

- PostgreSQL remains the source of truth
- session timelines remain append-only
- outbox-before-side-effects still governs dispatch
- artifact blobs stay off the control-plane event stream

## Scaling surfaces

- event-log partitioning by tenant and time window
- outbox indexing around pending versus acknowledged dispatch intent
- projection hotset versus rolling-summary shaping
- artifact index partitioning by tenant and retention class

## Proof expectations

Synthetic growth fixtures must show:

- bounded projector lag
- bounded outbox backlog
- bounded artifact-index freshness
- retention and partitioning strategies that preserve replay and audit semantics

## Anti-patterns

- replacing Postgres with a warehouse for control-plane truth
- storing large binary blobs on the event stream
- inventing scale shortcuts that weaken replay or auditability
