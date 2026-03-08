    # PHASE-14 - Runtime conformance, deterministic simulation, and replay oracle

**Status:** completed

    ## Phase goal

    Turn Aegis from an implemented runtime into a provably consistent runtime.

    ## Why this phase exists

    The core runtime is already built. The next step is to formalize replay equivalence, determinism boundaries, and simulation-driven conformance so later upgrades and scale work can be proved instead of assumed.

    ## Scope

    - replay oracle and determinism taxonomy
    - deterministic simulation scenarios
    - cross-language contract conformance
    - replay differential harnesses
    - benchmark corpus and correctness scorecards
    - fixture authoring flow for simulation and replay assets

    ## Non-goals

    - theorem proving
    - full browser emulation
    - generic model evaluation tooling
    - extension marketplace work

    ## Prerequisites

    PHASE-13

    ## Deliverables

    - replay oracle and determinism catalogs
    - phase-14 replay-equivalence gate
    - simulation DSL, deterministic runner, and simulation gate
    - cross-language contract conformance fixtures, report schema, and gate
    - replay differential harness, manifest, and gate
    - deterministic benchmark corpus, budgets, and generated scorecard
    - developer scaffold flow and runbook for simulation fixtures

    ## Detailed tasks

    - `P14-T01` - Define replay oracle and determinism taxonomy
    - `P14-T02` - Build scenario DSL and deterministic simulation runner
    - `P14-T03` - Build cross-language contract conformance suite
    - `P14-T04` - Build replay differential harness across versions and failure paths
    - `P14-T05` - Create benchmark corpus and correctness scorecards
    - `P14-T06` - Ship developer simulation kit and fixture authoring flow

    ## Dependencies

    - prerequisites: PHASE-13
    - unlocks after exit: none yet

    ## Risks

    - simulator drift from real runtime behavior
    - false confidence from incomplete replay equivalence rules
    - overbuilding lab infrastructure before it improves runtime change safety

    ## Test plan

    - `TS-004` - Replay and checkpoint determinism tests (`python3 scripts/run_elixir_suite.py TS-004`)
    - `TS-019` - Replay oracle and determinism validation (`pytest tests/replay_oracle -q`)
    - `TS-020` - Deterministic simulation validation (`pytest tests/simulation -q`)
    - `TS-021` - Contract conformance validation (`pytest tests/conformance -q`)
    - `TS-022` - Replay differential validation (`pytest tests/replay_diff -q`)
    - `TS-023` - Benchmark corpus and scorecard validation (`pytest tests/benchmarks -q`)
    - `TS-024` - Simulation fixture authoring-flow validation (`pytest tests/scaffolding -q`)

    ## Acceptance criteria

    - `AC-057` - Replay equivalence rules define what current-state equality means across full replay, checkpoint-tail replay, and historical replay.
    - `AC-058` - Determinism classes explicitly separate recomputable state, captured nondeterministic evidence, and externally unknowable state.
    - `AC-059` - The phase-14 replay-equivalence gate is machine-checkable and references concrete docs, schemas, metadata, and tests.
    - `AC-060` - Deterministic simulation scenarios, the canonical fault matrix, and a simulation runner exist as machine-checkable assets tied to replay and recovery work.
    - `AC-061` - Cross-language contract conformance fixtures cover dispatch, cancel, progress, heartbeat, and terminal worker lifecycle messages against the canonical transport topology.
    - `AC-062` - Replay diff fixtures compare current results against current and previous supported baselines and block on structured divergence.
    - `AC-063` - Benchmark corpus inputs, deterministic budgets, and the generated correctness scorecard are reproducible from committed fixtures.
    - `AC-064` - Contributors can scaffold a valid deterministic simulation fixture and validate it end to end through an explicit documented workflow.

    ## Exit criteria

    - critical-path replay-oracle and simulation-foundation tasks are implemented or intentionally deferred with justification;
    - linked tests for this phase pass;
    - linked acceptance criteria are satisfied;
    - generated tasks/traceability artifacts are refreshed;
    - no later-phase scope was pulled forward without an ADR-backed reason.

    ## What becomes unlocked after this phase

    none yet
