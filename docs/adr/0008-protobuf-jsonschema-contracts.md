# ADR-0008 — Protobuf for runtime contracts, JSON Schema for tool I/O

- Status: accepted
- Date: 2026-03-07

## Context

Runtime envelopes need strong typing, while tool inputs/outputs need flexible, schema-driven shapes.

## Decision

Use Protobuf for core runtime messages and JSON Schema for tool descriptors and payloads.

## Consequences

Using only ad hoc JSON would create drift; forcing everything into Protobuf would make tool extensibility clumsy.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
