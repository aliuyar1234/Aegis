    # PHASE-05 — Browser worker wedge baseline: read-only flows, artifacts, and resumable handles

    **Status:** implemented

    ## Phase goal

    Build the browser wedge baseline without permitting effectful writes yet.

    ## Why this phase exists

    Aegis needs browser proof early, but dangerous browser mutations must wait for policy and tokens.

    ## Scope

    - read-only browser flows
- artifact registration
- resumable handles
- fixtures

    ## Non-goals

    - effectful writes
- capability token checks
- approval-gated mutation

    ## Prerequisites

    PHASE-04

    ## Deliverables

    - browser worker baseline
- artifact metadata
- fixture set

    ## Detailed tasks

    - `P05-T01` — Implement Python browser worker package skeleton with Playwright lifecycle for read-only flows
- `P05-T02` — Implement signed artifact upload, immutable artifact metadata registration, and content hashing
- `P05-T03` — Implement resumable browser handle model and restart-safe metadata
- `P05-T04` — Implement example read-only browser workflows for account lookup and billing inspection
- `P05-T05` — Document browser baseline boundaries, mutation taxonomy, and fixture contracts

    ## Dependencies

    - prerequisites: PHASE-04
    - unlocks after exit: PHASE-06

    ## Risks

    - accidental write support sneaking in too early
- weak artifact evidence

    ## Test plan

    - `TS-007` — Browser wedge baseline and fixture tests (`pytest tests/browser_e2e -q`)

    ## Acceptance criteria

    - `AC-020` — Browser baseline supports read-only navigation, extraction, verification, artifact capture, and resumable handle metadata without effectful writes.
- `AC-021` — Artifact uploads bypass the control-plane bus and register immutable artifact metadata with content hash, tenancy, retention, and redaction fields.
- `AC-022` — Resumable browser handles, stable-page markers, and recovery metadata are persisted strongly enough for later recovery phases.
- `AC-023` — Browser workflow fixtures, mutation classifications, and uncertainty fixtures exist and validate against schemas.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-06
