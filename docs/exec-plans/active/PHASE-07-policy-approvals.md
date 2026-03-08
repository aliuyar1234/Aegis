    # PHASE-07 — Policy, approvals, capability tokens, and dangerous-action defaults

    **Status:** planned

    ## Phase goal

    Make effectful action dispatch safe through policy, approvals, and capability tokens.

    ## Why this phase exists

    Dangerous actions cannot be bolted on after browser work already exists.

    ## Scope

    - tool descriptors
- risk classes
- policy evaluation
- approval binding
- capability tokens

    ## Non-goals

    - browser chaos work
- full multitenancy implementation

    ## Prerequisites

    PHASE-04, PHASE-06

    ## Deliverables

    - tool registry
- approval request flow
- token claims schema

    ## Detailed tasks

    - `P07-T01` — Implement tool descriptor registry and JSON Schema validation path
- `P07-T02` — Implement policy evaluator and default risk classes including dangerous browser writes
- `P07-T03` — Implement approval requests, approval hashing, expiration, and operator decision flow
- `P07-T04` — Implement scoped capability tokens for effectful tool execution
- `P07-T05` — Document dangerous-action boundaries and approval defaults for browser mutations

    ## Dependencies

    - prerequisites: PHASE-04, PHASE-06
    - unlocks after exit: PHASE-08, PHASE-09, PHASE-10

    ## Risks

    - vague approvals
- token claims that are too weak or too broad

    ## Test plan

    - `TS-009` — Policy, approval, and capability-token tests (`pytest tests/policy -q`)
- `TS-011` — Security, multitenancy, and trust-boundary tests (`pytest tests/security -q`)

    ## Acceptance criteria

    - `AC-028` — Tool descriptors are explicit, versioned, validated against JSON Schema, and mapped to executor kind, risk class, idempotency, timeout, and scopes.
- `AC-029` — Policy decisions are explicit allow / allow_with_constraints / require_approval / deny outcomes and are recorded before effectful dispatch.
- `AC-030` — Approval requests bind to exact action hash, lease epoch, expiry, actor identity, and risk evidence.
- `AC-031` — Capability tokens for effectful actions bind tenant, workspace, session, action, tool, approved argument digest, expiry, and side-effect class.
- `AC-032` — Dangerous browser mutations default to approval or explicit allow-with-constraints and are listed in machine-readable dangerous-action catalogs.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-08, PHASE-09, PHASE-10
