# ADR-0004 — Sessions are deeply event-sourced; the whole platform is not

- Status: accepted
- Date: 2026-03-07

## Context

The session boundary needs append-only history, but the rest of the system does not need universal event sourcing.

## Decision

Event-source session timelines and action history; use ordinary relational models elsewhere.

## Consequences

Event-sourcing everything would add cost and complexity without improving the central runtime guarantees.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
