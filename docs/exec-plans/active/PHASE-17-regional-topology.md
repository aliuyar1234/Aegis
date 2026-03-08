# PHASE-17 - Regional topology, fault domains, and session mobility

**Status:** completed

## Phase goal

Make regional failure handling explicit by modeling fault domains, region-aware placement,
controlled evacuation, and session continuity across promotion boundaries without
violating the single-owner invariant.

## Why this phase exists

PHASE-15 proved upgrade and restore discipline, and PHASE-16 made fleet behavior
explicit under load. The next maturity step is turning regional posture into a bounded,
evidence-backed control-plane surface rather than a hand-waved future scale story.

## Scope

- regional topology profiles and fault-domain taxonomy
- region-aware placement and failover routing policy
- controlled regional evacuation and promotion drills
- session mobility continuity for checkpoints, approvals, and artifacts
- regional readiness evidence bundle

## Non-goals

- active-active multi-writer authority
- live session migration with simultaneous regional owners
- region-agnostic placement shortcuts that hide fault-domain semantics
- reinterpreting JetStream or workers as canonical regional truth

## Prerequisites

PHASE-15 and PHASE-16

## Deliverables

- machine-readable regional topology profiles and fault-domain catalog
- region-aware placement policy and deterministic routing examples
- evacuation drill fixtures and promotion runbooks
- session mobility manifest for checkpoint, approval, and artifact continuity
- regional evidence bundle tying topology, placement, evacuation, and mobility proof together

## Detailed tasks

- `P17-T01` - Define regional topology profiles and fault-domain catalog
- `P17-T02` - Implement region-aware placement and failover routing policy
- `P17-T03` - Build regional evacuation and failover drill harness
- `P17-T04` - Model session mobility, approval continuity, and artifact lineage
- `P17-T05` - Gate regional readiness on topology, evacuation, and mobility evidence

## Dependencies

- prerequisites: PHASE-15, PHASE-16
- unlocks after exit: none yet

## Risks

- allowing regional failover language to imply active-active ownership
- failing to bind approvals and artifacts to the same continuity guarantees as checkpoints
- promoting standby regions without bounded evidence about placement and evacuation assumptions

## Test plan

- `TS-037` - Regional topology and fault-domain validation (`pytest tests/regional_failover/test_phase17_topology_assets.py -q`)
- `TS-038` - Region-aware placement validation (`pytest tests/regional_failover/test_phase17_placement_assets.py -q`)
- `TS-039` - Regional evacuation and failover validation (`pytest tests/regional_failover/test_phase17_evacuation_assets.py -q`)
- `TS-040` - Session mobility and continuity validation (`pytest tests/regional_failover/test_phase17_mobility_assets.py -q`)
- `TS-041` - Regional evidence-bundle validation (`pytest tests/regional_failover/test_phase17_regional_evidence_assets.py -q`)

## Acceptance criteria

- `AC-077` - Regional topology profiles and fault-domain catalogs explicitly define region roles, promotion preconditions, evacuation boundaries, and warm-standby semantics without active-active authority.
- `AC-078` - Region-aware placement policies route sessions and execution pools by fault domain, tenant tier, and topology state while preserving the single-owner invariant.
- `AC-079` - Regional evacuation and failover drills model fencing, restore, and bounded promotion evidence instead of ad hoc incident steps.
- `AC-080` - Session mobility surfaces preserve checkpoint lineage, approval binding, and artifact continuity during controlled regional evacuation without live multi-owner behavior.
- `AC-081` - Regional readiness is modeled as a reproducible evidence bundle across topology, placement, evacuation, and mobility proof surfaces.

## Exit criteria

- the phase-17 regional topology, placement, evacuation, mobility, and evidence artifacts exist and validate;
- the task graph, acceptance registry, suite registry, and generated artifacts are synchronized;
- regional phase-gate fixtures prove the failover posture is machine-checkable rather than prose-only;
- the active phase points at phase-17 tasks rather than the completed phase-16 backlog.

## What becomes unlocked after this phase

none yet
