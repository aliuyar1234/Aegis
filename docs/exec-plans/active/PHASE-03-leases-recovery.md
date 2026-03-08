    # PHASE-03 — Lease ownership, fencing, and recovery semantics

    **Status:** implemented

    ## Phase goal

    Enforce exactly one live owner per session and make adoption/fencing semantics explicit.

    ## Why this phase exists

    Without lease correctness, everything built on top is unsafe.

    ## Scope

    - leases
- epochs
- adoption
- self-fencing
- recovery hooks

    ## Non-goals

    - worker dispatch
- browser work

    ## Prerequisites

    PHASE-02

    ## Deliverables

    - lease model
- owner adoption flow
- fenced/degraded mode

    ## Detailed tasks

    - `P03-T01` — Implement lease persistence and renewal model in Postgres
- `P03-T02` — Integrate lease epochs into SessionKernel command acceptance and event emission
- `P03-T03` — Implement adoption path after lease expiry or node loss
- `P03-T04` — Implement self-fencing behavior and degraded mode on lease ambiguity
- `P03-T05` — Write runbook-backed recovery scenarios for node loss and lease ambiguity

    ## Dependencies

    - prerequisites: PHASE-02
    - unlocks after exit: PHASE-04

    ## Risks

    - split-brain ownership
- stale owner side effects

    ## Test plan

    - `TS-005` — Lease, fencing, and adoption tests (`python3 scripts/run_elixir_suite.py TS-005`)
- `TS-010` — Recovery, uncertainty, and chaos tests (`pytest tests/recovery tests/chaos -q`)

    ## Acceptance criteria

    - `AC-012` — Exactly one authoritative live owner can advance a session at a time, enforced by lease epoch checks.
- `AC-013` — Node loss or lease expiry triggers adoption without silent duplicate authoritative owners or silent side effects.
- `AC-014` — Owners self-fence on lease ambiguity and surface degraded/fenced state to operators and runbooks.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-04
