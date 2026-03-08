# Disaster Recovery

## Purpose

This document frames PHASE-15 restore and recovery work as evidence-backed drills,
not just aspirational operational guidance.

## Canonical machine-readable artifact

- `meta/recovery-objectives.yaml`

## Recovery surfaces

- truth-store restore
- checkpoint integrity
- replay-tail recovery
- artifact inventory reconciliation

## Design rules

- recovery objectives must be explicit
- restore success must include integrity evidence, not only service availability
- recovery must preserve authoritative ownership boundaries
