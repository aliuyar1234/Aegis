# ADR-0015 — Testing, documentation, and anti-drift rules are first-class assets

- Status: accepted
- Date: 2026-03-07

## Context

Aegis is too architecturally sensitive to rely on implicit tribal knowledge.

## Decision

Maintain machine-readable invariants, phase gates, task metadata, traceability, runbooks, and quality checks in-repo.

## Consequences

Without anti-drift mechanics, later Codex runs will erode the architecture even if early decisions were sound.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
