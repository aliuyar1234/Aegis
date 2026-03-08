# PHASE-16 - Fleet scheduling, isolation, and SLO-driven operability

**Status:** completed

## Phase goal

Make Aegis predictable under sustained load by formalizing capacity, placement,
overload doctrine, isolation response, growth plans, and fleet-level operator evidence.

## Why this phase exists

Replay, upgrade, and recovery credibility are now modeled and gated. The next step
is turning fleet behavior into an explicit control-plane discipline instead of something
teams only learn during tenant pressure or operator escalations.

## Scope

- capacity model and bounded SLO profiles
- placement policy and execution-pool taxonomy
- adaptive admission control and load-shedding doctrine
- noisy-neighbor isolation and hot-tenant mitigation
- storage/outbox/projection/artifact-index growth planning
- fleet triage surfaces and reproducible operator evidence bundles

## Non-goals

- ML-driven scheduling or autoscaling heuristics
- cross-region live session migration
- replacing PostgreSQL as the source of truth
- AI-generated operator summaries without evidence bundles

## Prerequisites

PHASE-14 and PHASE-15

## Deliverables

- machine-readable SLO profiles and overload policies
- deterministic placement policy with pool taxonomy fixtures
- load-shedding and hot-tenant isolation reports
- storage-growth planning fixtures and scaling reports
- fleet-triage product surface and reproducible operator evidence bundle

## Detailed tasks

- `P16-T01` - Define capacity model, SLO profiles, and overload doctrine
- `P16-T02` - Implement session placement engine and pool taxonomy
- `P16-T03` - Build adaptive admission control and load shedding
- `P16-T04` - Implement noisy-neighbor isolation and hot-tenant mitigation
- `P16-T05` - Formalize storage and transport scaling plan
- `P16-T06` - Add fleet forensics and operator evidence bundles

## Dependencies

- prerequisites: PHASE-14, PHASE-15
- unlocks after exit: none yet

## Risks

- tuning around undefined budgets instead of explicitly modeling budgets first
- accidental coupling of correctness invariants to scheduler or scaling shortcuts
- operator-facing fleet views that summarize away the evidence needed for action

## Test plan

- `TS-031` - Capacity-model and SLO-profile validation (`pytest tests/performance/test_phase16_capacity_assets.py -q`)
- `TS-032` - Placement policy and pool-taxonomy validation (`pytest tests/placement -q`)
- `TS-033` - Load-shedding and overload-doctrine validation (`pytest tests/load_shedding -q`)
- `TS-034` - Noisy-neighbor isolation validation (`pytest tests/noisy_neighbor -q`)
- `TS-035` - Storage-growth and transport-scaling validation (`pytest tests/performance/storage_growth -q`)
- `TS-036` - Fleet triage and operator-evidence validation (`pytest tests/operator_fleet -q`)

## Acceptance criteria

- `AC-071` - Capacity profiles, SLI/SLO targets, and overload doctrine are explicit for critical control-plane and execution-plane paths.
- `AC-072` - Placement policy and execution-pool taxonomy make routing deterministic and explainable across tenant tier, fault domain, and capability constraints.
- `AC-073` - Admission control and load-shedding rules protect operator-critical, recovery, and effectful execution paths under overload.
- `AC-074` - Noisy-neighbor isolation profiles identify causing tenants or workflow classes and define bounded mitigation responses.
- `AC-075` - Storage and transport scaling surfaces model growth for truth-store, outbox, projections, and artifact indexes without weakening runtime truth invariants.
- `AC-076` - Fleet triage surfaces provide cohort-level failure clustering and reproducible operator evidence bundles.

## Exit criteria

- the phase-16 capacity, placement, overload, isolation, scaling, and fleet-evidence artifacts exist and validate;
- the task graph, acceptance registry, suite registry, and generated artifacts are synchronized;
- phase-gate fixtures prove the fleet-operability surface is machine-checkable rather than prose-only;
- the active phase points at phase-16 tasks rather than the completed phase-15 backlog.

## What becomes unlocked after this phase

none yet
