# ADR-0013 — Three multitenancy isolation tiers from day one

- Status: accepted
- Date: 2026-03-07

## Context

Enterprise usage will demand different isolation levels, but the runtime core should stay coherent.

## Decision

Support Tier A shared, Tier B isolated execution, and Tier C dedicated deployments as architectural targets.

## Consequences

Deferring multitenancy design would force painful rework in storage, routing, and security.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
