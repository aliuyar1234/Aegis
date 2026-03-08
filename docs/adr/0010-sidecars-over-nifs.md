# ADR-0010 — Sidecars over NIFs for hot paths and low-level execution

- Status: accepted
- Date: 2026-03-07

## Context

The BEAM control plane must stay healthy under load and failure.

## Decision

Run performance-critical, media, and protocol-heavy code in sidecars (mostly Rust) instead of nontrivial NIFs.

## Consequences

Hot NIFs risk scheduler starvation and collapse the isolation model.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
