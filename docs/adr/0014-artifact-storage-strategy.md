# ADR-0014 — Artifacts are immutable blobs in S3-compatible storage

- Status: accepted
- Date: 2026-03-07

## Context

Screenshots, DOM dumps, traces, and recordings are large and often sensitive.

## Decision

Store blobs in object storage via signed URLs, keep only metadata and references in the control plane.

## Consequences

Moving blobs through the control plane or storing them inline in timelines would create performance and privacy problems.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
