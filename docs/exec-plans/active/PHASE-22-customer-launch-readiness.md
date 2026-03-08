# PHASE-22 - Customer golden paths, launch signoff, and support/security baseline

**Status:** completed

## Phase goal

Turn the pre-customer launch checklist into explicit, reproducible launch-readiness
surfaces: real customer golden paths, release signoff, security baseline, and
support operations.

## Why this phase exists

PHASE-21 made first-clone onboarding and evaluation deployment explicit, but a
team can still install a strong system without yet having the evidence needed to
put it responsibly in front of customers. The next launch wave has to bind actual
customer workflows, signoff criteria, security controls, and support ownership
into committed repo artifacts.

## Scope

- two canonical customer golden paths
- launch signoff binding release evidence, restore drills, rollback, and evaluation
- machine-checkable launch security baseline
- machine-checkable support operating model
- launch readiness evidence bundle

## Non-goals

- production billing or pricing surfaces
- customer success CRM workflows
- managed-cloud automation
- new runtime features unrelated to launch readiness
- broad UI polish detached from customer-operability proof

## Prerequisites

PHASE-15, PHASE-19, PHASE-20, and PHASE-21

## Deliverables

- customer golden-path manifest for a read-heavy browser flow and an approval-gated browser write flow
- release signoff manifest with evidence, restore, rollback, and evaluation references
- launch security baseline manifest
- support operating model manifest
- launch readiness evidence bundle

## Detailed tasks

- `P22-T01` - Define canonical customer golden paths for read-heavy and approval-gated browser operations
- `P22-T02` - Build launch signoff surfaces binding release evidence, restore drills, and rollback runbooks
- `P22-T03` - Establish the launch security baseline across supply chain, secrets, signing, and defaults
- `P22-T04` - Define the support operating model with severities, escalation, and customer communications
- `P22-T05` - Gate launch readiness on golden paths, signoff, security baseline, and support evidence

## Dependencies

- prerequisites: PHASE-15, PHASE-19, PHASE-20, PHASE-21
- unlocks after exit: none yet

## Risks

- presenting "customer ready" workflows that are not bound to committed adoption and evidence surfaces
- treating release signoff as prose instead of a reproducible artifact
- leaving security and support as policy aspirations instead of concrete launch gates

## Test plan

- `TS-059` - Customer golden-path validation (`pytest tests/launch_readiness/test_phase22_customer_golden_paths_assets.py -q`)
- `TS-060` - Launch signoff validation (`pytest tests/launch_readiness/test_phase22_release_signoff_assets.py -q`)
- `TS-061` - Security baseline validation (`pytest tests/launch_readiness/test_phase22_security_baseline_assets.py -q`)
- `TS-062` - Support model validation (`pytest tests/launch_readiness/test_phase22_support_model_assets.py -q`)
- `TS-063` - Launch readiness evidence-bundle validation (`pytest tests/launch_readiness/test_phase22_launch_readiness_evidence_assets.py -q`)

## Acceptance criteria

- `AC-099` - Customer launch readiness includes two explicit golden paths, one read-heavy and one approval-gated write path, each bound to starter kits, deployment tracks, replay, and operator intervention surfaces.
- `AC-100` - Release signoff is modeled as a reproducible surface that binds release evidence, restore drills, rollback runbooks, and evaluation workflow targets.
- `AC-101` - Security baseline coverage is machine-checkable across dependency audit, SBOM, secret scanning, signed artifacts, hardened defaults, scoped credentials, and documented key rotation.
- `AC-102` - Support operations define severity classes, response windows, on-call ownership, escalation paths, and customer communication templates instead of relying on implicit founder support.
- `AC-103` - Launch readiness is captured as a reproducible evidence bundle across customer golden paths, signoff, security baseline, and support model surfaces.

## Exit criteria

- the phase-22 manifests, docs, runner scripts, and gates exist and validate;
- `make launch-check` produces passing signoff and evidence results;
- golden customer workflows remain anchored to committed starter kits and deployment tracks;
- support and security launch surfaces are explicit enough to hand to a new operator or evaluator without live explanation.

## What becomes unlocked after this phase

none yet
