# PHASE-18 - Certified ecosystem, governed extensions, and public compatibility leadership

**Status:** completed

## Phase goal

Turn the extension surface into a certified, sandboxed, compatibility-governed ecosystem
with reproducible public-facing evidence instead of ad hoc partner exceptions.

## Why this phase exists

PHASE-10 created the bounded extension contract, and PHASE-14 through PHASE-17
made replay, recovery, fleet, and regional guarantees explicit. The next maturity step
is making third-party adoption defensible by tying extension admission to certification,
sandbox posture, delegated governance, and benchmark-backed compatibility publication.

## Scope

- extension certification levels and signed compatibility-report shape
- sandbox profiles for connectors, artifact processors, and edge adapters
- delegated-governance policy bundles with rollback discipline
- benchmark-backed public compatibility tracks for certified extension packs
- ecosystem evidence bundle proving certification, sandboxing, governance, and publication surfaces

## Non-goals

- a marketplace UI
- unbounded connector proliferation
- direct extension writes into canonical runtime state
- replacing operator evidence with prose-only partner review
- promising active runtime protocol takeover to MCP or connector surfaces

## Prerequisites

PHASE-10, PHASE-14, and PHASE-17

## Deliverables

- machine-readable certification levels and candidate pack enrollment
- sandbox-profile catalog and extension-to-profile assignments
- policy-bundle profiles for delegated extension governance
- public benchmark and compatibility manifest for certified tracks
- reproducible ecosystem evidence bundle

## Detailed tasks

- `P18-T01` - Define extension certification levels and signed compatibility reports
- `P18-T02` - Implement sandbox profiles and extension isolation assignments
- `P18-T03` - Define policy-bundle profiles and delegated-governance surfaces
- `P18-T04` - Publish benchmark-backed public compatibility tracks for certified extension packs
- `P18-T05` - Gate ecosystem readiness on certification, sandbox, governance, and public evidence

## Dependencies

- prerequisites: PHASE-10, PHASE-14, PHASE-17
- unlocks after exit: none yet

## Risks

- turning certification into vague partner process instead of a machine-checkable surface
- allowing sandbox-profile language to drift into permission sprawl
- publishing compatibility claims that are not tied to replay, benchmark, and governance evidence

## Test plan

- `TS-042` - Extension certification validation (`pytest tests/extensions_conformance/test_phase18_certification_assets.py -q`)
- `TS-043` - Sandbox-profile validation (`pytest tests/sandbox_profiles -q`)
- `TS-044` - Policy-bundle validation (`pytest tests/policy_bundles -q`)
- `TS-045` - Public compatibility-track validation (`pytest tests/extensions_conformance/test_phase18_public_compatibility_assets.py -q`)
- `TS-046` - Ecosystem evidence-bundle validation (`pytest tests/extensions_conformance/test_phase18_ecosystem_evidence_assets.py -q`)

## Acceptance criteria

- `AC-082` - Extension certification levels explicitly define review requirements, signing posture, recertification windows, and candidate-pack enrollment for the supported ecosystem surface.
- `AC-083` - Sandbox profiles bound network posture, secret volume, extension kind, and MCP eligibility for each admitted extension fixture.
- `AC-084` - Policy bundles define delegated-governance inputs, dual-control rules, rollback discipline, and explanation fields instead of relying on ad hoc reviewer knowledge.
- `AC-085` - Public compatibility tracks tie certified extension packs to bounded benchmark classes, compatibility dimensions, and publication requirements without implying runtime bypass.
- `AC-086` - Ecosystem readiness is modeled as a reproducible evidence bundle across certification, sandbox, policy, and public compatibility reports.

## Exit criteria

- the phase-18 certification, sandbox, policy-bundle, public-compatibility, and evidence artifacts exist and validate;
- the task graph, acceptance registry, suite registry, generated artifacts, and phase registry remain synchronized;
- phase-18 gates prove the ecosystem-governance surface is machine-checkable rather than partner-process prose;
- the active phase points at phase-18 rather than the completed phase-17 backlog.

## What becomes unlocked after this phase

none yet
