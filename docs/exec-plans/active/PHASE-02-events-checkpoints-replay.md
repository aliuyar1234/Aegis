    # PHASE-02 — Event log, checkpoints, and replay

    **Status:** implemented

    ## Phase goal

    Make the session timeline real through append-only events, checkpoints, and replay.

    ## Why this phase exists

    Recovery, audit, and operator trust depend on replayable history and checkpoint correctness.

    ## Scope

    - event store
- outbox
- checkpoint schema
- replay engine
- event payload coverage

    ## Non-goals

    - leases
- browser work
- operator UI

    ## Prerequisites

    PHASE-01

    ## Deliverables

    - atomic append/outbox path
- checkpoint serialization
- historical replay semantics

    ## Detailed tasks

    - `P02-T01` — Implement Postgres schemas and migrations for sessions, events, checkpoints, and outbox
- `P02-T02` — Implement atomic append + seq_no + hash chain + outbox write
- `P02-T03` — Implement structured checkpoint serialization and restoration
- `P02-T04` — Implement replay engine for recovery and historical replay without external re-execution
- `P02-T05` — Create replay determinism fixtures and golden timeline examples

    ## Dependencies

    - prerequisites: PHASE-01
    - unlocks after exit: PHASE-03, PHASE-04

    ## Risks

    - schema drift in event payloads
- replay requiring external re-execution

    ## Test plan

    - `TS-004` — Replay and checkpoint determinism tests (`python3 scripts/run_elixir_suite.py TS-004`)

    ## Acceptance criteria

    - `AC-008` — Event append, seq_no assignment, hash chaining, and outbox write happen in one atomic transaction.
- `AC-009` — Checkpoint payloads conform to the checkpoint schema and hydrate state from latest checkpoint plus tail events.
- `AC-010` — Historical replay rebuilds from recorded events and artifacts without re-executing models, browsers, or external APIs.
- `AC-011` — Every registered event type maps to a typed payload schema and explicit version in the event catalog.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-03, PHASE-04
