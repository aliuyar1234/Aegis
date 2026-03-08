    # PHASE-11 — Voice and media expansion path

    **Status:** deferred

    ## Phase goal

    Define a concrete future voice/media path that preserves the runtime thesis.

    ## Why this phase exists

    Voice/media is deferred, but the repo must already make later implementation legible and bounded.

    ## Scope

    - media contracts
- Rust sidecar boundaries
- QoS degradation policy
- voice/media gate

    ## Non-goals

    - shipping live telephony

    ## Prerequisites

    PHASE-10

    ## Deliverables

    - media topology docs
- future contract stubs
- media phase gate

    ## Detailed tasks

    - `P11-T01` — Define Rust sidecar contracts for media, protocol, and recording hot paths
- `P11-T02` — Define session state extensions for streaming media and degraded-mode handoff
- `P11-T03` — Define operator console deltas for future voice/media sessions
- `P11-T04` — Create voice/media phase-gate fixtures, media topology docs, and operator/runbook deltas for degraded QoS paths

    ## Dependencies

    - prerequisites: PHASE-10
    - unlocks after exit: PHASE-13

    ## Risks

    - voice/media handwaving
- sidecar boundaries drifting back into BEAM

    ## Test plan

    - `TS-015` — Voice/media boundary tests (`pytest tests/media -q`)

    ## Acceptance criteria

    - `AC-045` — Voice/media contracts preserve session ownership, replay, and policy boundaries while moving hot paths into Rust sidecars.
- `AC-046` — Media transport, recording, artifact, and degraded-mode policies are specified with their own topology and runbooks.
- `AC-047` — A machine-checkable voice/media phase gate exists and references concrete fixtures and contracts.
- `AC-048` — Voice/media capacity isolation, QoS degradation, and operator handoff rules are explicit.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-13
