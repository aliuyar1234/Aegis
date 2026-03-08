    # PHASE-13 — Cloud and enterprise hardening

    **Status:** current

    ## Phase goal

    Make enterprise hardening implementation-grade rather than aspirational.

    ## Why this phase exists

    Dedicated deployments, key isolation, compliance controls, and enterprise gates require explicit artifacts.

    ## Scope

    - enterprise isolation
- audit export
- retention
- control matrix
- enterprise gate

    ## Non-goals

    - every compliance certification

    ## Prerequisites

    PHASE-09, PHASE-11, PHASE-12

    ## Deliverables

    - enterprise control matrix
- dedicated tenant evidence bundle
- enterprise readiness gate

    ## Detailed tasks

    - `P13-T01` — Implement audit export and redaction workflows tied to event and artifact models
- `P13-T02` — Define dedicated deployment and key-isolation path for Tier C tenants
- `P13-T03` — Define retention classes, archival policy, and operational SLO surfaces
- `P13-T04` — Create enterprise acceptance checklist and release gate
- `P13-T05` — Create enterprise control matrix, dedicated-tenant evidence bundle, and enterprise readiness gate assets

    ## Dependencies

    - prerequisites: PHASE-09, PHASE-11, PHASE-12
    - unlocks after exit: none

    ## Risks

    - enterprise claims with no artifact-backed proof

    ## Test plan

    - `TS-017` — Enterprise readiness validation (`pytest tests/enterprise -q`)

    ## Acceptance criteria

    - `AC-052` — Enterprise tiers specify dedicated deployment, key isolation, artifact controls, and data residency hooks.
- `AC-053` — Enterprise auth, secrets, audit export, retention, and redaction paths are defined as implementation-ready requirements.
- `AC-054` — The enterprise readiness phase gate is machine-checkable and references concrete controls, docs, and runbooks.
- `AC-055` — Late-phase docs, tasks, generated artifacts, and validation rules remain synchronized under the anti-drift policy.
- `AC-056` — OPEN_DECISIONS.md contains only bounded, explicitly justified unresolved items and no hidden placeholder drift.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    none
