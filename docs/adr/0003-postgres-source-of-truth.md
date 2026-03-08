# ADR-0003 — PostgreSQL is the canonical source of truth

- Status: accepted
- Date: 2026-03-07

## Context

Aegis needs transactional durability for sessions, events, checkpoints, approvals, and leases.

## Decision

Use Postgres as the system of record; workers and buses are secondary systems that consume committed intent.

## Consequences

Using the message bus or worker-local state as truth would break auditability, replay, and deterministic recovery.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
