    # PHASE-04 — Worker contracts, transport topology, and execution bridge

    **Status:** implemented

    ## Phase goal

    Lock the cross-language execution boundary before large-scale worker work begins.

    ## Why this phase exists

    Transport and contract drift are the fastest path to distributed spaghetti.

    ## Scope

    - Protobuf contracts
- JetStream topology
- Execution Bridge
- worker registry
- timeouts/heartbeats/cancel

    ## Non-goals

    - effectful browser writes
- operator approvals

    ## Prerequisites

    PHASE-02, PHASE-03

    ## Deliverables

    - transport topology SSOT
- codegen config
- Execution Bridge semantics

    ## Detailed tasks

    - `P04-T01` — Finalize Protobuf envelopes and generate contract packages for Elixir/Python/Rust consumption
- `P04-T02` — Implement Execution Bridge with JetStream subjects, request/accept flow, and async result callbacks
- `P04-T03` — Implement worker registration, heartbeat, timeout, and cancellation semantics
- `P04-T04` — Implement error taxonomy, idempotency metadata propagation, and trace context handling
- `P04-T05` — Enforce worker read/write boundaries and add guardrails against canonical DB access

    ## Dependencies

    - prerequisites: PHASE-02, PHASE-03
    - unlocks after exit: PHASE-05, PHASE-06, PHASE-07

    ## Risks

    - subject invention
- redelivery ambiguity
- worker access to canonical DB

    ## Test plan

    - `TS-002` — Contract, schema, event payload, and transport validation (`python3 scripts/validate_schemas.py`)
- `TS-006` — Execution bridge and transport contract tests (`python3 scripts/run_elixir_suite.py TS-006`)

    ## Acceptance criteria

    - `AC-015` — JetStream topology, routing keys, streams, consumers, headers, and ack/redelivery semantics are explicit in docs and machine-readable topology files.
- `AC-016` — Execution Bridge supports dispatch, accept, heartbeat, progress, completion, failure, timeout, and cancellation using the locked transport contracts.
- `AC-017` — Contract codegen for Protobuf bindings is configured and reproducible for Elixir, Python, and Rust.
- `AC-018` — Trace context propagates across API, SessionKernel, outbox, JetStream, workers, and artifact registration.
- `AC-019` — Execution-plane components are prevented by architecture and validation rules from writing canonical control-plane tables.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-05, PHASE-06, PHASE-07
