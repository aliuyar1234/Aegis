# Capacity model

## Purpose

PHASE-16 makes fleet behavior explicit instead of emergent. The control plane should
have declared SLO profiles, protected classes, and overload doctrine before anyone
tries to tune scheduling or autoscaling around production pain.

## Model

The model is intentionally bounded:

- SLOs are attached to named profiles, not improvised per-incident.
- Profiles bind to budget manifests in `meta/performance-budgets.yaml`.
- Every profile references an overload policy in `meta/load-shed-policies.yaml`.
- Protected classes always include operator control, recovery, and already-approved
  effectful work.

## Critical paths

The phase-16 capacity model treats these as first-class:

- session admission to authoritative owner
- committed outbox intent to worker dispatch acknowledgement
- projector freshness for operator views
- artifact-index freshness for investigation
- cohort-query latency for fleet triage

## Anti-patterns

- treating queue growth as a debugging surprise instead of a modeled trigger
- tuning with no declared budget profile
- starving operator or recovery work to preserve background convenience jobs
- hiding overload in generic "system busy" language without policy or evidence
