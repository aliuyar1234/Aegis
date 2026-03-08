# aegis_events

## Purpose

Event append, replay, checkpointing, and timeline integrity.

## Responsibilities

- canonical event envelopes
- append-only per-session ordering and hash chaining
- structured checkpoint rows
- outbox rows written in the same transaction boundary
- hydrate replay and historical replay without external re-execution
- Postgres-backed persistence for sessions, events, checkpoints, and outbox
- the shared `Aegis.Repo` boundary used by control-plane persistence apps

## Must not own

- hidden authoritative runtime state outside the event timeline boundary
- lease ownership semantics
- transport dispatch itself
- browser or worker execution logic

## Phase 02 modules

- `Aegis.Repo` - canonical Postgres repo
- `Aegis.Events.Store` - atomic append/checkpoint/outbox store backed by Postgres
- `Aegis.Events.Replay` - hydrate and historical replay reducer
- `Aegis.Events.Envelope` - durable timeline envelope
- `Aegis.Events.Schema` - canonical table map
