# ADR-0001 — Session is the primary runtime abstraction

- Status: accepted
- Date: 2026-03-07

## Context

Aegis is a runtime for long-lived AI sessions, not a request handler or chat shell.

## Decision

Make Session the canonical control-plane unit with its own lifecycle, state, timeline, checkpoints, approvals, and operator surface.

## Consequences

Treating requests, chat threads, or jobs as the primary abstraction would make recovery, ownership, and replay fragmented and inconsistent.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
