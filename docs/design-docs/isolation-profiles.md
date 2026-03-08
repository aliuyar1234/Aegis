# Isolation profiles

## Purpose

PHASE-16 extends multitenancy beyond quotas into noisy-neighbor isolation. The goal
is not bespoke tenant code paths. The goal is explicit profiles that detect pressure,
attribute it, and preserve unaffected budgets.

## Isolation units

Profiles may target:

- a tenant
- a workflow class
- a dedicated deployment lane

## Mitigation options

The bounded mitigation space includes:

- throttling new session admission
- pinning hot traffic to isolated pools
- delaying replay and backfill workloads
- suspending non-critical historical indexing

## What must stay preserved

Isolation cannot break:

- operator control
- recovery
- approved effectful execution
- dedicated audit export lanes where promised

## Anti-patterns

- hand-edited tenant exceptions in code
- using isolation to hide uncontrolled scaling debt
- preserving throughput by violating control-plane invariants
