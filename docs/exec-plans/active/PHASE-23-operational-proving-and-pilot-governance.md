# PHASE-23 - Operational proving, customer environment readiness, and pilot launch governance

**Status:** completed

## Phase goal

Turn the remaining pre-customer launch gaps into explicit, machine-checkable workstreams:
real-infrastructure proving, launch observability, customer environment acceptance,
customer-facing operating docs, and design-partner pilot governance.

## Why this phase exists

PHASE-22 made launch readiness legible inside the repo, but the broader pre-customer
launch checklist still has open edges that are not satisfied by repo-native evidence
alone. Aegis still needs explicit proving surfaces for production-like drills,
operator telemetry, customer environment acceptance, external-facing operating docs,
and the actual first-customer go/no-go path.

## Scope

- real-infrastructure proving for restore, rollback, upgrade, and tenant isolation
- launch observability and alerting baseline
- customer environment readiness and acceptance checklist
- customer-facing operating and failure-mode docs
- design-partner pilot governance and go/no-go evidence bundle

## Non-goals

- managed-cloud automation beyond launch-proof needs
- generic analytics or warehouse work
- pricing, billing, or commercial packaging
- new runtime features unrelated to launch proving
- broad UI polish detached from launch operability

## Prerequisites

PHASE-15, PHASE-16, PHASE-20, PHASE-21, and PHASE-22

## Deliverables

- a real-infrastructure proving program definition
- an explicit launch observability and alerting workstream
- a customer environment readiness acceptance surface
- a customer-facing operations package definition
- a design-partner pilot governance surface
- a phase-23 launch governance evidence bundle

## Detailed tasks

- `P23-T01` - Define the real-infrastructure proving program for restore, rollback, upgrade, and tenant isolation
- `P23-T02` - Define the launch observability and alerting baseline for operators and support
- `P23-T03` - Define customer environment readiness and the launch acceptance checklist
- `P23-T04` - Define the customer-facing operations package for install, upgrade, limits, failure modes, and responsibilities
- `P23-T05` - Build design-partner pilot governance and gate pre-customer launch on a go/no-go evidence bundle

## Dependencies

- prerequisites: PHASE-15, PHASE-16, PHASE-20, PHASE-21, PHASE-22
- unlocks after exit: none yet

## Risks

- calling repo-native launch surfaces "customer ready" without real proving in infrastructure
- leaving observability and customer environment acceptance as implied operator knowledge
- allowing the first-customer launch motion to remain founder-memory process instead of governed evidence

## Test plan

- `TS-064` - Real-infrastructure proving validation (`pytest tests/launch_readiness/test_phase23_real_infrastructure_proving_assets.py -q`)
- `TS-065` - Launch observability validation (`pytest tests/launch_readiness/test_phase23_launch_observability_assets.py -q`)
- `TS-066` - Customer environment readiness validation (`pytest tests/launch_readiness/test_phase23_customer_environment_readiness_assets.py -q`)
- `TS-067` - Customer operations package validation (`pytest tests/launch_readiness/test_phase23_customer_operations_package_assets.py -q`)
- `TS-068` - Pilot governance and launch evidence validation (`pytest tests/launch_readiness/test_phase23_pilot_governance_assets.py -q`)

## Acceptance criteria

- `AC-104` - PHASE-23 defines a machine-checkable real-infrastructure proving workstream for backup, PITR, restore, rollback, rolling-upgrade, and tenant-isolation evidence in production-like environments.
- `AC-105` - PHASE-23 defines an explicit observability and alerting baseline covering session ownership, replay health, checkpoint lag, outbox health, worker health, artifact failures, approval backlog, and degraded-mode entry.
- `AC-106` - PHASE-23 defines customer environment readiness as an explicit acceptance surface covering DNS, certificates, secrets, storage, backups, alerts, and operational responsibilities.
- `AC-107` - PHASE-23 defines the customer-facing operations package for installation, deployment, upgrade, limits, failure modes, and operator responsibilities as a bounded launch workstream instead of diffuse follow-up docs.
- `AC-108` - PHASE-23 defines design-partner pilot governance and captures pre-customer launch decision evidence as a reproducible go/no-go bundle.

## Exit criteria

- the phase-23 manifests, docs, runner scripts, gates, and evidence bundle exist and validate
- `make prelaunch-check` produces passing proving, observability, environment, operations, and pilot results
- the remaining pre-customer launch gaps are modeled as explicit machine-checkable repo surfaces rather than implied follow-up

## What becomes unlocked after this phase

none yet
