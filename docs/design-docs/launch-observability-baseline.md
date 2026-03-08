# Launch observability baseline

This document defines the minimum operator telemetry and alerting baseline required
before Aegis is treated as pre-customer-launch ready.

## Required signals

- session ownership
- replay health
- checkpoint lag
- outbox health
- worker health
- artifact upload failures
- approval backlog
- degraded-mode entry

## Constraint

Observability coverage must be explicit enough that a support engineer can identify
which dashboard, alert, SLO profile, and runbook applies without relying on the
core authors being present.
