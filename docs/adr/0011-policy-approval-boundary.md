# ADR-0011 — Policy and approval boundaries sit before effectful dispatch

- Status: accepted
- Date: 2026-03-07

## Context

Aegis must be explicit about what is allowed, denied, or approval-gated before touching external systems.

## Decision

Evaluate policy on action requests and bind approvals to exact action hashes and lease epochs before dispatch.

## Consequences

Post-dispatch approvals or vague approvals would destroy auditability and operator trust.

## What this locks

This decision is part of the locked baseline for Aegis. Any later change must update:
- this ADR
- affected design docs
- task metadata
- traceability
- acceptance criteria and tests where applicable

## Rejected alternatives

Alternatives were considered only where relevant, but this repository treats the chosen direction as the default unless a fatal contradiction is discovered.
