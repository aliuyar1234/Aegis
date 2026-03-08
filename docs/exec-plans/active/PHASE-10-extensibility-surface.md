    # PHASE-10 — Extensibility surface, connector SDK, and compatibility policy

    **Status:** current

    ## Phase goal

    Expose a real extensibility surface without surrendering runtime control.

    ## Why this phase exists

    Extensions and connectors are strategic, but only if they are bounded and versioned.

    ## Scope

    - connector SDK
- extension lifecycle
- compatibility policy
- MCP adapter boundary

    ## Non-goals

    - treating MCP as internal runtime protocol

    ## Prerequisites

    PHASE-09

    ## Deliverables

    - extension contracts
- compatibility tests
- sample connector pack

    ## Detailed tasks

    - `P10-T01` — Define extension contracts for new tools, connectors, and artifact processors
- `P10-T02` — Define MCP adapter boundary without making MCP the internal runtime protocol
- `P10-T03` — Create compatibility and versioning policy for third-party extensions
- `P10-T04` — Create sample extension pack layout and review rubric

    ## Dependencies

    - prerequisites: PHASE-09
    - unlocks after exit: PHASE-11, PHASE-12

    ## Risks

    - extension APIs bypassing core invariants

    ## Test plan

    - `TS-014` — Extensibility and connector compatibility tests (`pytest tests/extensibility -q`)

    ## Acceptance criteria

    - `AC-042` — Connector and extension contracts define lifecycle hooks, version ranges, capability boundaries, and artifact processor interfaces.
- `AC-043` — Third-party extension compatibility rules are machine-checkable and supported by sample connector fixtures.
- `AC-044` — MCP is treated as an external adapter boundary, not the internal runtime protocol.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-11, PHASE-12
