    # PHASE-12 — OSS core versus managed platform split

    **Status:** completed

    ## Phase goal

    Define what becomes OSS core and what remains managed-platform value.

    ## Why this phase exists

    The split affects packaging, release process, extension expectations, and long-term moat.

    ## Scope

    - OSS core manifest
- managed-only surfaces
- packaging matrix
- upgrade policy

    ## Non-goals

    - actual hosted platform rollout

    ## Prerequisites

    PHASE-10

    ## Deliverables

    - split-surface manifest
- packaging matrix
- OSS/managed gate

    ## Detailed tasks

    - `P12-T01` — Define what belongs in OSS core versus managed cloud services
- `P12-T02` — Define packaging and deployment flavors for shared, isolated-execution, and dedicated control plane modes
- `P12-T03` — Document release, upgrade, and compatibility policy for the split
- `P12-T04` — Create OSS core manifest, managed-only surface catalog, and packaging matrix artifacts
- `P12-T05` — Create split-surface release manifests, upgrade policy artifacts, and OSS/managed phase gate

    ## Dependencies

    - prerequisites: PHASE-10
    - unlocks after exit: PHASE-13

    ## Risks

    - ambiguous packaging and unsupported migration paths

    ## Test plan

    - `TS-016` — OSS/managed split validation (`pytest tests/packaging -q`)

    ## Acceptance criteria

    - `AC-049` — The OSS core surface is explicitly bounded from managed-only control-plane services, packages, and operational features.
- `AC-050` — Packaging, release, and upgrade matrices exist for OSS, shared cloud, isolated execution, and dedicated deployment flavors.
- `AC-051` — Split-surface compatibility policy covers contracts, migrations, and operator-facing documentation obligations.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-13
