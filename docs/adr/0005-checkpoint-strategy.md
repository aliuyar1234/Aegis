# ADR-0005 — Structured checkpoints plus tail replay

- Status: accepted
- Date: 2026-03-07

## Context

Genesis replay alone is too slow and too brittle for long-lived sessions.

## Decision

Store structured, inspectable checkpoints at meaningful boundaries and replay only the event tail during hydrate.

## Consequences

Opaque or absent checkpoints would slow recovery and make debugging harder.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
