# Region-aware placement

## Purpose

PHASE-17 extends placement from pool selection into region selection. It remains
policy-driven and deterministic.

## Rules

- healthy topology prefers the declared primary region
- failover topology may route only to declared standby regions
- tenant tier and topology profile remain first-class inputs
- region-aware placement still preserves the single-owner invariant

## Canonical machine-readable artifact

- `meta/regional-placement-policies.yaml`

## Anti-patterns

- hidden cross-region fallback
- region selection that ignores topology state
- using regional placement to imply live mobility without fencing
