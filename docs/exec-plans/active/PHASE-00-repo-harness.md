    # PHASE-00 — Foundations, repository harness, local development, and anti-drift tooling

    **Status:** completed

    ## Phase goal

    Harden the repository itself as a trustworthy Codex execution harness.

    ## Why this phase exists

    Codex cannot safely build Aegis if the SSOT, task graph, validators, and local stack are ambiguous.

    ## Scope

    - root docs
- machine-readable metadata
- validators
- local stack bootstrap
- prompt pack

    ## Non-goals

    - runtime implementation
- browser automation
- operator console features

    ## Prerequisites

    none

    ## Deliverables

    - current-phase state
- generated artifact pipeline
- link/schema/traceability validators
- local Compose stack with init
- phase-gate scaffolds

    ## Detailed tasks

    - `P00-T01` — Create the repository SSOT and agent map
- `P00-T02` — Create machine-readable invariants, phase gates, acceptance, and traceability data
- `P00-T03` — Create local dev stack for Postgres, NATS, MinIO, and Jaeger scaffolding
- `P00-T04` — Create validators and CI workflows for repo, contracts, and traceability
- `P00-T05` — Create prompt pack and starting sequence for bounded Codex execution

    ## Dependencies

    - prerequisites: none
    - unlocks after exit: PHASE-01

    ## Risks

    - drift between docs and metadata
- phase ordering ambiguity
- fake or stale generated files

    ## Test plan

    - `TS-001` — Repo structure, link integrity, phase state, and anti-drift validation (`python3 scripts/validate_repo.py`)
- `TS-002` — Contract, schema, event payload, and transport validation (`python3 scripts/validate_schemas.py`)
- `TS-013` — Generated artifact freshness tests (`python3 scripts/generate_docs.py --check`)

    ## Acceptance criteria

    - `AC-001` — Repository validation succeeds for required paths, internal markdown links, forbidden-phrase checks, and current-phase coherence.
- `AC-002` — AGENTS.md stays concise, references current-phase state, and points only to repository sources of truth.
- `AC-003` — Local bootstrap initializes Postgres, JetStream streams/consumers, MinIO bucket(s), and OTEL-to-Jaeger wiring without undocumented manual steps.
- `AC-004` — Generated task and traceability artifacts are reproducible and freshness-checked in CI and local validation.

    ## Exit criteria

    - all critical-path tasks for this phase are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    PHASE-01
