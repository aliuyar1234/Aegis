    # PHASE-09 — Multitenancy, quotas, authz, audit, and trust boundaries

    **Status:** planned

    ## Phase goal

    Productize the trust boundary with tenancy, quotas, authz, and audit.

    ## Why this phase exists

    Enterprise credibility requires explicit isolation and control, not assumptions.

    ## Scope

    - tiers A/B/C
- quotas
- RBAC/ABAC
- audit/redaction

    ## Non-goals

    - extension marketplace
- voice/media

    ## Prerequisites

    PHASE-07, PHASE-08

    ## Deliverables

    - tenant-aware routing model
- role/attribute catalogs
- audit paths

    ## Detailed tasks

    - `P09-T01` — Enforce tenant/workspace scoping across tables, contracts, and events
- `P09-T02` — Implement quotas and admission control for sessions, browser contexts, and effectful actions
- `P09-T03` — Implement tiered worker-pool isolation and routing metadata
- `P09-T04` — Integrate RBAC/ABAC checks into operator and API control surfaces
- `P09-T05` — Update threat models and security docs based on implementation realities

    ## Dependencies

    - prerequisites: PHASE-07, PHASE-08
    - unlocks after exit: PHASE-10, PHASE-13

    ## Risks

    - cross-tenant leakage
- unbounded concurrency

    ## Test plan

    - `TS-011` — Security, multitenancy, and trust-boundary tests (`pytest tests/security -q`)

    ## Acceptance criteria

    - `AC-038` — Tenancy tiers A/B/C are represented in storage, worker routing, artifact keyspaces, and operator surfaces.
- `AC-039` — Admission control and quotas are enforced for live sessions, concurrent browser contexts, and concurrent effectful actions.
- `AC-040` — OIDC-ready auth plus RBAC/ABAC catalogs govern operator and API control surfaces with tenant/workspace scoping.
- `AC-041` — Audit, redaction, and dangerous-action evidence paths are defined and traceable to runtime events and artifacts.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-10, PHASE-13
