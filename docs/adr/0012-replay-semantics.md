# ADR-0012 — Historical replay consumes recorded nondeterministic outputs

- Status: accepted
- Date: 2026-03-07

## Context

Models, browsers, APIs, and humans are nondeterministic. Replay must stay useful anyway.

## Decision

Use recorded events and artifacts for historical replay; add counterfactual sandbox replay later if needed.

## Consequences

Replaying by re-calling external systems would produce misleading and irreproducible results.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
