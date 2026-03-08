    # PHASE-06 — Operator console and session inspection baseline

    **Status:** current

    ## Phase goal

    Give operators a stable, replayable window into session truth.

    ## Why this phase exists

    Aegis is only credible if humans can inspect what the runtime thinks is happening.

    ## Scope

    - fleet view
- session detail view
- replay surfaces
- operator intervention events

    ## Non-goals

    - policy decisions themselves
- effectful mutation flows

    ## Prerequisites

    PHASE-04, PHASE-05

    ## Deliverables

    - stable operator session view contract
- replay timeline baseline
- intervention controls

    ## Detailed tasks

    - `P06-T01` — Implement live session list, filters, and system health overview
- `P06-T02` — Implement session detail view with owner, state, in-flight actions, approvals, and checkpoints
- `P06-T03` — Implement artifact viewer and timeline scrubber for historical replay
- `P06-T04` — Implement operator join, note, pause, abort, takeover, and return-control flows
- `P06-T05` — Write operator-console product spec deltas as implementation converges

    ## Dependencies

    - prerequisites: PHASE-04, PHASE-05
    - unlocks after exit: PHASE-07

    ## Risks

    - UI-only state
- projections missing owner/deadline/wait information

    ## Test plan

    - `TS-008` — Operator console and projection tests (`mix test test/operator_console`)

    ## Acceptance criteria

    - `AC-024` — Operator session view contracts include owner node, lease epoch, wait reason, deadlines, approvals, in-flight actions, artifacts, and recovery markers.
- `AC-025` — Timeline and replay UX consume stable projection data and recorded artifacts rather than hidden UI-only state.
- `AC-026` — Operator join, note, pause, abort, and takeover actions are represented as runtime events with no shadow control path.
- `AC-027` — Operator-facing runbooks and console surfaces are linked for recovery, uncertainty, and approval waits.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-07
