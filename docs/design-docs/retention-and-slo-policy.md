# Retention and SLO policy

This document defines the PHASE-13 retention, archival, and operational SLO posture.

## Goal

Turn retention and archival from scattered metadata into an explicit enterprise policy with clear degraded responses.

## Canonical policy

The machine-readable policy lives in `meta/retention-slo-policy.yaml`.

## Retention classes

The locked classes are:

- hot operational events
- long-lived audit events
- short-lived debug artifacts
- customer artifacts
- redacted payload stubs

These classes extend the existing artifact `retention_class` model rather than replacing it.

## Archival doctrine

- timeline history is never rewritten for retention convenience
- archive restore requires metadata integrity
- redaction preserves audit meaning through stubs and state markers

## Enterprise SLO surfaces

Phase 13 makes these SLO surfaces explicit:

- hot replay load
- on-demand audit export bundle preparation
- redaction completion
- archived artifact restore

Every SLO must define a degraded response rather than quietly timing out in the background.

## Runbook consequence

Retention or archive lag is an operator-visible failure mode.

Use `docs/runbooks/retention-backlog.md` when archive movement, restore latency, or redaction completion drifts outside the bounded policy.
