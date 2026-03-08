# ADR-0009 — Browser-backed service operations is the first wedge

- Status: accepted
- Date: 2026-03-07

## Context

Aegis needs a proof surface that stresses durability, artifacts, approvals, and human takeover.

## Decision

Start with browser service operations against messy admin surfaces and internal tools.

## Consequences

Voice is compelling but adds severe latency and protocol demands too early; generic chat proves too little.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
