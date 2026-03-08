# ADR-0007 — NATS JetStream is the cross-language dispatch fabric

- Status: accepted
- Date: 2026-03-07

## Context

Aegis needs durable async transport with request/reply patterns and controlled buffering.

## Decision

Use NATS JetStream for cross-language commands, progress, and completion events; keep Postgres as the source of truth.

## Consequences

Kafka is heavier than needed for this control-plane pattern; synchronous RPC alone would over-couple the runtime.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
