    # PHASE-01 — Session kernel and state model

    **Status:** implemented

    ## Phase goal

    Implement the SessionKernel and its authoritative process boundaries before any transport-heavy work.

    ## Why this phase exists

    Everything else depends on stable ownership of session lifecycle, state, and process roles.

    ## Scope

    - session lifecycle
- supervisor tree
- durable vs ephemeral state split
- stable projection fields

    ## Non-goals

    - transport implementation
- browser worker logic
- policy/approval dispatch

    ## Prerequisites

    PHASE-00

    ## Deliverables

    - SessionKernel state model
- supervisor structure
- projection contract baseline

    ## Detailed tasks

    - `P01-T01` — Create Elixir umbrella app boundaries and ownership docs as code-adjacent scaffolding
- `P01-T02` — Implement SessionKernel state model, lifecycle transitions, and durable/ephemeral separation
- `P01-T03` — Implement canonical per-session supervisor tree and child process responsibilities
- `P01-T04` — Implement command handlers that emit in-memory events and projection updates
- `P01-T05` — Add module-level docs and golden examples for session process ownership

    ## Dependencies

    - prerequisites: PHASE-00
    - unlocks after exit: PHASE-02

    ## Risks

    - mixing durable and ephemeral state
- leaking authority into child processes

    ## Test plan

    - `TS-003` — Session state model tests (`python3 scripts/run_elixir_suite.py TS-003`)

    ## Acceptance criteria

    - `AC-005` — SessionKernel implements provisioning, hydrating, active, waiting, cancelling, and terminal transitions with explicit wait reasons.
- `AC-006` — The per-session supervisor tree and process ownership boundaries match the locked runtime model.
- `AC-007` — Durable and ephemeral session state are separated, and the stable session projection fields are defined before downstream UI work begins.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-02
