    # PHASE-08 — Effectful browser flows, uncertainty handling, resilience, and demo gates

    **Status:** planned

    ## Phase goal

    Turn the browser wedge into a realistic, failure-aware system with effectful writes and demo gates.

    ## Why this phase exists

    This is where the runtime starts proving real-world credibility.

    ## Scope

    - effectful browser writes
- uncertain side effects
- duplicate suppression
- chaos/recovery
- internal/public demos

    ## Non-goals

    - tenant isolation tiers
- connector ecosystem

    ## Prerequisites

    PHASE-05, PHASE-06, PHASE-07

    ## Deliverables

    - effectful browser workflows
- uncertainty model
- machine-checkable demo gates

    ## Detailed tasks

    - `P08-T01` — Implement duplicate completion suppression and action uncertainty classification
- `P08-T02` — Implement quarantine flows for event corruption, replay failure, and repeated hydrate crashes
- `P08-T03` — Implement browser instability recovery playbook hooks and degraded-mode surfacing
- `P08-T04` — Create and automate chaos and recovery scenarios for internal demo acceptance
- `P08-T05` — Create public demo script and acceptance artifact set
- `P08-T06` — Implement effectful browser mutation flows with approval-bound writes, capability tokens, before/after artifacts, and uncertainty surfacing

    ## Dependencies

    - prerequisites: PHASE-05, PHASE-06, PHASE-07
    - unlocks after exit: PHASE-09

    ## Risks

    - silent duplicate writes
- uncertainty hidden from operators

    ## Test plan

    - `TS-007` — Browser wedge baseline and fixture tests (`pytest tests/browser_e2e -q`)
- `TS-010` — Recovery, uncertainty, and chaos tests (`pytest tests/recovery tests/chaos -q`)
- `TS-012` — Phase-gate scenario validation (`python3 scripts/run_phase_gate.py tests/phase-gates/internal-demo.yaml tests/phase-gates/public-demo.yaml`)

    ## Acceptance criteria

    - `AC-033` — Effectful browser mutation flows run only after policy, approval, and capability-token checks and capture before/after artifacts.
- `AC-034` — Duplicate terminal completions are deduplicated, and uncertain side effects are surfaced for human review instead of silent retry.
- `AC-035` — Worker crash, browser instability, transport lag, datastore degradation, and event corruption paths are modeled, tested, and reflected in runbooks.
- `AC-036` — The internal demo phase gate is machine-checkable and passes against the committed gate spec and fixtures.
- `AC-037` — The public demo phase gate is machine-checkable and passes against the committed gate spec and fixtures.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-09
