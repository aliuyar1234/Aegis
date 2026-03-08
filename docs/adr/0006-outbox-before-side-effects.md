# ADR-0006 — Commit intent and outbox before side effects

- Status: accepted
- Date: 2026-03-07

## Context

Aegis must never dispatch external work based only on in-memory state.

## Decision

Append events and outbox rows transactionally; publish and dispatch from the outbox.

## Consequences

Ad hoc dispatch after commit or before commit would create lost commands and ghost side effects.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
