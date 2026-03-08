# Standby Topology

## Purpose

PHASE-15 adds a warm-standby control-plane profile and the promotion expectations
needed to keep recovery honest.

## Canonical machine-readable artifact

- `meta/topology-profiles.yaml`

## Design rules

- standby promotion is controlled and fenced
- restore and promotion evidence must align
- single-owner guarantees survive promotion

## Non-goals

- cross-region active-active authority
- live session migration during this phase
