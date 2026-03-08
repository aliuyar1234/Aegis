# PHASE-15 - Upgrade safety, schema evolution, and disaster recovery

**Status:** completed

## Phase goal

Make version changes, rolling upgrades, restores, and standby promotion boring and
evidence-backed.

## Why this phase exists

Aegis now has a replay oracle, deterministic simulation, and conformance surfaces.
The next credibility step is proving that the runtime can evolve across versions,
survive upgrades, and recover from restore paths without violating its invariants.

## Scope

- compatibility matrix and version-skew policy
- event and checkpoint upcaster manifests
- rolling upgrade semantics and drain/adopt strategy
- backup, PITR, and restore-drill harnesses
- warm-standby topology and promotion evidence
- release gates based on compatibility and recovery evidence

## Non-goals

- active-active multi-writer control plane
- arbitrary permanent backward compatibility promises
- cloud-vendor-specific recovery lock-in
- live session migration across active regions

## Prerequisites

PHASE-14

## Deliverables

- machine-readable compatibility matrix and skew rules
- upcaster manifest registry and schema-evolution design surface
- rolling-upgrade strategy catalog and runbook
- recovery objectives and restore-drill artifacts
- topology profiles and standby-promotion evidence surface
- release-evidence gate definitions for upgrade and recovery discipline

## Detailed tasks

- `P15-T01` - Define compatibility matrix and version-skew policy
- `P15-T02` - Build event/checkpoint upcaster pipeline
- `P15-T03` - Implement rolling upgrade and lease-safe drain/adopt protocol
- `P15-T04` - Build backup, PITR, and restore-drill harness
- `P15-T05` - Add warm-standby topology and promotion evidence
- `P15-T06` - Gate releases on compatibility and recovery evidence

## Dependencies

- prerequisites: PHASE-14
- unlocks after exit: none yet

## Risks

- version-skew gaps that look safe until replay is exercised
- false confidence from incomplete restore drills
- recovery procedures that preserve data but violate single-owner guarantees

## Test plan

- `TS-025` - Compatibility matrix and skew-policy validation (`pytest tests/compatibility -q`)
- `TS-026` - Upcaster manifest and migration-asset validation (`pytest tests/migrations -q`)
- `TS-027` - Rolling-upgrade asset validation (`pytest tests/upgrade_dr -q`)
- `TS-028` - Disaster-recovery and restore-objective validation (`pytest tests/disaster_recovery -q`)
- `TS-029` - Standby-topology and promotion-surface validation (`pytest tests/topology -q`)
- `TS-030` - Release-evidence gate validation (`pytest tests/release_evidence -q`)

## Acceptance criteria

- `AC-065` - Compatibility windows and denied version-skew combinations are explicit for runtime, workers, schemas, checkpoints, policies, and extensions.
- `AC-066` - Historical event and checkpoint versions map to explicit upcaster manifests instead of hidden migration assumptions.
- `AC-067` - Rolling-upgrade strategy artifacts define lease-safe drain, adopt, and mixed-version safety boundaries.
- `AC-068` - Recovery objectives and restore-drill surfaces define evidence-backed PITR and artifact-reconciliation expectations.
- `AC-069` - Standby-topology profiles and promotion gates preserve the single-owner invariant during controlled recovery.
- `AC-070` - Release evidence is modeled as a gateable artifact that depends on compatibility, upgrade, and restore proof surfaces.

## Exit criteria

- the phase-15 machine-readable upgrade and DR artifacts exist and validate;
- the task graph, acceptance, and suite registry are synchronized;
- generated task and traceability artifacts are refreshed;
- the active phase points at phase-15 tasks rather than the completed phase-14 backlog.

## What becomes unlocked after this phase

none yet
