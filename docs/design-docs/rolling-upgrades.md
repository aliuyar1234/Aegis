# Rolling Upgrades

## Purpose

PHASE-15 defines the control-plane expectations for mixed-version rollout, node drain,
lease-safe adoption, and worker compatibility during controlled upgrades.

## Canonical machine-readable artifact

- `meta/upgrade-strategies.yaml`

## Design rules

- exactly one authoritative owner remains the invariant during upgrades
- drain and adopt behavior must be explicit before nodes are removed
- mixed-version windows are bounded by the compatibility matrix

## Non-goals

- active-active multi-writer topologies
- hidden topology redesign under the name of upgrade work
