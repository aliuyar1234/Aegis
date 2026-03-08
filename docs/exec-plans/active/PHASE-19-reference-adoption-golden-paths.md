# PHASE-19 - Reference adoption, operator drills, and golden-path starter kits

**Status:** completed

## Phase goal

Turn Aegis from a rigorously validated runtime into a safely adoptable platform by
making first-adopter profiles, reference deployment tracks, operator training drills,
and golden-path starter kits explicit and reproducible.

## Why this phase exists

PHASE-18 made ecosystem admission governable, but serious adoption still depends on
tribal knowledge unless the repo publishes bounded onboarding and operations paths.
This phase turns adoption into a machine-checkable surface rather than a founder-led
process.

## Scope

- adoption profiles for distinct first-adopter classes
- reference deployment tracks tied to already implemented flavor, topology, and SLO surfaces
- operator training and incident exercise manifests
- golden-path starter kits that package certified extension packs with simulation and governance guidance
- adoption evidence bundle proving the whole surface is reproducible

## Non-goals

- a customer-facing marketplace
- broad product marketing collateral
- replacing runtime evidence with tutorials alone
- introducing a second orchestration model for onboarding paths
- weakening existing policy, replay, or single-owner invariants for convenience

## Prerequisites

PHASE-15, PHASE-16, PHASE-17, and PHASE-18

## Deliverables

- machine-readable adoption profiles and first-adopter readiness rules
- reference deployment-track catalog for shared and dedicated rollouts
- operator training exercise manifest with bounded runbook references
- golden-path starter-kit manifest for certified extension-pack adoption
- reproducible adoption evidence bundle

## Detailed tasks

- `P19-T01` - Define adoption profiles and first-adopter readiness rules
- `P19-T02` - Implement reference deployment tracks for shared and dedicated rollouts
- `P19-T03` - Build operator training and incident exercise manifests
- `P19-T04` - Create golden-path starter kits for certified extension packs
- `P19-T05` - Gate adoption readiness on profiles, tracks, drills, and starter-kit evidence

## Dependencies

- prerequisites: PHASE-15, PHASE-16, PHASE-17, PHASE-18
- unlocks after exit: none yet

## Risks

- turning adoption guidance into prose that drifts from the actual runtime contracts
- allowing starter kits to imply hidden product defaults outside policy and sandbox boundaries
- teaching operators through scenario fragments that do not line up with committed evidence surfaces

## Test plan

- `TS-047` - Adoption profile validation (`pytest tests/adoption/test_phase19_adoption_profiles_assets.py -q`)
- `TS-048` - Reference deployment-track validation (`pytest tests/adoption/test_phase19_reference_tracks_assets.py -q`)
- `TS-049` - Operator exercise validation (`pytest tests/operator_training -q`)
- `TS-050` - Golden-path starter-kit validation (`pytest tests/starter_kits -q`)
- `TS-051` - Adoption evidence-bundle validation (`pytest tests/adoption/test_phase19_adoption_evidence_assets.py -q`)

## Acceptance criteria

- `AC-087` - Adoption profiles tie adopter classes to bounded deployment tracks, required evidence, operator drills, and onboarding runbooks.
- `AC-088` - Reference deployment tracks bind deployment flavors, topology surfaces, SLO profiles, and public compatibility tracks instead of relying on implicit environment lore.
- `AC-089` - Operator exercise manifests define bounded drills with runbook references, evidence prerequisites, and expected outcomes linked to already implemented failure and governance surfaces.
- `AC-090` - Golden-path starter kits package certified extension packs, sandbox and policy bindings, simulation scenarios, and deployment guidance without implying runtime bypass.
- `AC-091` - Adoption readiness is modeled as a reproducible evidence bundle across adoption profiles, reference tracks, operator drills, and starter kits.

## Exit criteria

- the phase-19 adoption-profile, reference-track, operator-drill, starter-kit, and evidence artifacts exist and validate;
- the task graph, acceptance registry, suite registry, generated artifacts, and phase registry remain synchronized;
- phase-19 gates prove adoption readiness is machine-checkable rather than founder-memory guidance;
- the active phase points at phase-19 rather than the completed phase-18 backlog.

## What becomes unlocked after this phase

none yet
