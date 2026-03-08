# Regional topology

## Purpose

PHASE-17 makes regional posture explicit. Aegis is still a single-authority runtime,
so regional work must describe how authority moves, not how multiple regions own
the same session at once.

## Rules

- exactly one authoritative region may advance a session at a time
- standby regions are promotion targets, not concurrent control-plane writers
- promotion requires fenced primary behavior plus restore evidence
- regional topology must be explicit for each supported tier

## Canonical machine-readable artifacts

- `meta/regional-topology-profiles.yaml`
- `meta/fault-domain-catalog.yaml`

## Anti-patterns

- active-active control-plane language
- region failover without explicit fencing
- vague "global" placement that hides fault domains
