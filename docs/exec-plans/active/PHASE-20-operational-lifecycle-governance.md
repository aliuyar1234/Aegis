# PHASE-20 - Operational lifecycle governance, rollout waves, and deprecation discipline

**Status:** completed

## Phase goal

Turn Aegis from a safely adoptable platform into a sustainably operated platform by
making operator accreditation, rollout-wave governance, incident-review packets,
and deprecation discipline explicit and reproducible.

## Why this phase exists

PHASE-19 made first adoption bounded and machine-checkable, but long-lived platform
operation still drifts toward tribal process unless the repo defines how operators
stay accredited, how rollout waves promote, how incidents are reviewed, and how
surfaces are sunset without silent breakage.

## Scope

- operator accreditation tracks and renewal rules
- rollout-wave manifests tied to committed deployment tracks and evidence surfaces
- incident-review packet manifests for customer and operator handoff
- deprecation and sunset governance for starter kits, rollout tracks, and certified extensions
- reproducible lifecycle evidence bundle proving the whole surface is coherent

## Non-goals

- generic HR training systems
- customer-success CRM workflows
- replacing runtime evidence with slide decks or summaries
- broad pricing or packaging changes
- weakening certified extension or deployment boundaries for convenience

## Prerequisites

PHASE-15, PHASE-16, PHASE-17, PHASE-18, and PHASE-19

## Deliverables

- operator accreditation manifest with bounded authority and renewal windows
- rollout-wave catalog for shared and dedicated deployment tracks
- incident-review packet manifest linked to exercises, evidence, and follow-up surfaces
- deprecation-governance manifest for rollout tracks, starter kits, and certified packs
- reproducible lifecycle evidence bundle

## Detailed tasks

- `P20-T01` - Define operator accreditation tracks and renewal rules
- `P20-T02` - Implement rollout-wave and change-window manifests for shared and dedicated deployments
- `P20-T03` - Build incident-review packet manifests and customer handoff evidence links
- `P20-T04` - Create deprecation and sunset governance for starter kits, tracks, and certified extensions
- `P20-T05` - Gate lifecycle readiness on accreditation, rollout, incident review, and deprecation evidence

## Dependencies

- prerequisites: PHASE-15, PHASE-16, PHASE-17, PHASE-18, PHASE-19
- unlocks after exit: none yet

## Risks

- drifting from runtime evidence into prose-only operations process
- letting accreditation imply hidden authority outside explicit operator and policy boundaries
- treating deprecation as announcement text instead of a bounded migration and freeze surface

## Test plan

- `TS-052` - Operator accreditation validation (`pytest tests/accreditation -q`)
- `TS-053` - Rollout-wave validation (`pytest tests/rollout -q`)
- `TS-054` - Incident-review packet validation (`pytest tests/incident_reviews -q`)
- `TS-055` - Deprecation governance validation (`pytest tests/lifecycle/test_phase20_deprecation_assets.py -q`)
- `TS-056` - Lifecycle evidence-bundle validation (`pytest tests/lifecycle/test_phase20_lifecycle_evidence_assets.py -q`)

## Acceptance criteria

- `AC-092` - Operator accreditation tracks bind exercises, required evidence, renewal cadence, and bounded authority to explicit deployment tracks.
- `AC-093` - Rollout-wave manifests bind deployment tracks, change windows, promotion criteria, and rollback surfaces instead of relying on implicit release lore.
- `AC-094` - Incident-review packet manifests define reproducible handoff evidence, source exercises, and follow-up references linked to committed runtime outputs.
- `AC-095` - Deprecation governance defines sunset windows, successor paths, freeze actions, and rollback boundaries for certified packs, starter kits, and rollout tracks.
- `AC-096` - Lifecycle readiness is modeled as a reproducible evidence bundle across accreditation, rollout, incident review, and deprecation surfaces.

## Exit criteria

- the phase-20 accreditation, rollout-wave, incident-review, deprecation, and evidence artifacts exist and validate;
- the task graph, acceptance registry, suite registry, generated artifacts, and phase registry remain synchronized;
- phase-20 gates prove operational lifecycle discipline is machine-checkable rather than process memory;
- the active phase points at phase-20 rather than the completed phase-19 backlog.

## What becomes unlocked after this phase

none yet
