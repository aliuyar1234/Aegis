# Placement engine

## Purpose

PHASE-16 introduces a deterministic placement policy for authoritative session owners
and execution pools. Placement is not a generic scheduler. It is a policy surface
that preserves the single-owner invariant while making routing explainable.

## Inputs

The canonical inputs are:

- tenant tier and isolation expectations
- required capability
- preferred fault domain
- active pool taxonomy
- explicit priority ordering

## Pool taxonomy

The pool taxonomy stays machine-readable in `meta/placement-policies.yaml`.
It distinguishes:

- shared browser pools
- isolated premium browser pools
- dedicated control-plane pools

Each pool advertises fault domain, supported tenant tiers, capabilities, and an
explicit priority.

## Rules

- prefer a tier-matched pool over a cheaper but less isolated fallback
- keep fault-domain locality when a compatible pool exists
- never let a worker pool become canonical truth; placement only chooses who may
  execute or own the session
- stay deterministic for identical inputs

## Anti-patterns

- hidden routing heuristics
- ML-based scheduling in place of explicit policy
- cross-region mobility sneaking into same-region placement work
