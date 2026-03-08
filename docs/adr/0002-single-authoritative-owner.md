# ADR-0002 — Exactly one authoritative live owner per session

- Status: accepted
- Date: 2026-03-07

## Context

Aegis must survive crashes and partitions without split-brain side effects.

## Decision

Use a lease-based single-owner model backed by Postgres, with lease epochs and self-fencing on ambiguity.

## Consequences

Relying on cluster presence or eventual coordination for authority would allow duplicate owners and unsafe writes.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
