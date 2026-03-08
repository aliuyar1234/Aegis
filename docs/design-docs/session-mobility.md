# Session mobility

## Purpose

Session mobility in Aegis is controlled continuity, not live multi-owner migration.
PHASE-17 defines what must remain intact when authority moves between regions.

## Continuity rules

- checkpoint lineage must remain intact
- approval continuity must be explicit
- artifact continuity must preserve immutable references and retention semantics
- authoritative region after mobility must be explicit

## Canonical machine-readable artifact

- `meta/session-mobility-manifest.yaml`

## Anti-patterns

- silently discarding approval context
- reconstructing artifact continuity from assumptions
- implying live active-active mobility
