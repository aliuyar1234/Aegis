# State-of-the-Art Roadmap Extension

## Purpose

This document captures the broader **post-PHASE-13 strategic extension** for Aegis Runtime.
PHASE-14, PHASE-15, PHASE-16, PHASE-17, PHASE-18, PHASE-19, PHASE-20, PHASE-21, PHASE-22, PHASE-23, PHASE-24, PHASE-25, and PHASE-26 have now been activated in the main SSOT planning surface.
This document remains useful for preserving the reasoning behind that extension.

Use this document for:

- wider roadmap design after the original PHASE-00 through PHASE-13 plan
- discussion about what would make Aegis genuinely state-of-the-art
- drafting successor phase plans and work-item slices after PHASE-26
Treat this as supporting architecture and planning context.
The active implementation SSOT still lives in the phase docs, task graph, and machine-readable
metadata.

## Current Assessment

### What is already strong

- The runtime shape is correct: session-first, single-owner, Postgres-backed, replayable, and explicitly split between truth, transport, and execution.
- The architecture is disciplined: Elixir owns authoritative runtime concerns; Python and Rust stay in the execution/data plane.
- Dangerous behavior is modeled, not deferred: approvals, capability tokens, dangerous-action classes, uncertainty handling, quarantine, degraded mode, and duplicate suppression are already present.
- The first wedge was chosen well: browser-backed service operations forced the runtime to solve artifact capture, risky writes, recovery, and operator takeover early.
- The repo discipline is unusually mature: schemas, SSOT metadata, phase gates, traceability, runbooks, threat models, and CI validation are part of the product surface.
- The implementation still reads like a durable control plane instead of collapsing into a generic orchestration wrapper.

### What is unusually strong

- Operators are first-class runtime participants instead of an afterthought.
- Uncertainty is modeled as runtime state instead of vague retry behavior.
- Capability-token and dangerous-action boundaries exist inside the runtime, not only in product workflows.
- Replay is an operational surface, not just a debugging convenience.
- Ownership of truth, transport, and execution is cleanly separated.
- The repo treats docs, tasks, tests, contracts, and invariants as engineering artifacts, not project decoration.

### What still prevents "state of the art"

The biggest missing pieces are **proof, operational maturity, and long-horizon rigor**.
The system can already do the right things.
What it still lacks is stronger machinery to prove that it will keep doing the right things under:

- version skew
- replay across evolving schemas
- rolling upgrades
- disaster recovery and restore drills
- large-tenant noisy-neighbor pressure
- regional fault domains
- extension ecosystem drift
- benchmark scrutiny

The next frontier is deeper rigor, not broader scope.

## Strategic Gaps

### Gap 1: Replay oracle and determinism discipline

- Why it matters: a durable runtime is only as credible as its replay guarantees.
- Why it is still open: replay exists, but replay equivalence across versions, checkpoints, and nondeterministic boundaries is not yet formalized.
- Recommended scope: full phase

### Gap 2: Simulation and conformance infrastructure

- Why it matters: state-of-the-art systems are adversarially exercised, not only implemented.
- Why it is still open: there is no full scenario DSL, fault-matrix simulator, or cross-language conformance lab continuously proving contracts.
- Recommended scope: full phase paired with replay rigor

### Gap 3: Upgrade safety and schema evolution rigor

- Why it matters: event-sourced systems become dangerous when versioning is informal.
- Why it is still open: contracts and schemas exist, but there is no full compatibility matrix, upcaster discipline, rolling-upgrade protocol, or release gate for skew safety.
- Recommended scope: full phase

### Gap 4: Disaster recovery and restore drills

- Why it matters: enterprise hardening is incomplete until restore is rehearsed and evidenced.
- Why it is still open: hardening exists, but PITR drills, artifact reconciliation, and standby-promotion evidence are not yet a system.
- Recommended scope: full phase paired with upgrade safety

### Gap 5: Fleet-scale placement and performance isolation

- Why it matters: quotas alone do not make load behavior predictable.
- Why it is still open: there is no placement engine, hot-tenant isolation strategy, or policy-driven overload doctrine.
- Recommended scope: full phase

### Gap 6: Operator excellence at fleet scale

- Why it matters: elite runtimes let operators reason across fleets, not only inspect one session at a time.
- Why it is still open: session inspection exists, but not differential replay, failure clustering, evidence bundles, or fleet triage.
- Recommended scope: task cluster inside the fleet-scale phase

### Gap 7: Regional topology and fault-domain maturity

- Why it matters: serious control planes need explicit fault-domain semantics.
- Why it is still open: dedicated deployment profiles exist, but region-aware placement, standby promotion semantics, and evacuation doctrine do not.
- Recommended scope: full phase

### Gap 8: Extension certification and ecosystem governance

- Why it matters: extensibility without certification becomes supply-chain chaos.
- Why it is still open: manifests and compatibility policies exist, but not certification, sandbox profiles, signed compatibility reports, or public conformance assets.
- Recommended scope: full phase

### Gap 9: Policy explainability and delegated governance

- Why it matters: enterprise trust matures from "policy exists" to "policy is explainable and governable."
- Why it is still open: runtime policy exists, but formal policy bundles, change control, dual control, and explainability artifacts are not yet a complete system.
- Recommended scope: task cluster inside the ecosystem/governance phase

### Gap 10: Benchmarkability as moat

- Why it matters: if Aegis becomes the thing people benchmark against, it stops being just another runtime.
- Why it is still open: there is no benchmark corpus, replay challenge suite, or public reliability scorecard.
- Recommended scope: task cluster beginning in conformance work

### Gap 11: Developer ergonomics for serious adopters

- Why it matters: runtime quality does not matter if extension and scenario authoring remain too expensive.
- Why it is still open: the repo is disciplined, but fixture authoring, simulation-first local workflows, and connector certification paths are not yet mature.
- Recommended scope: task cluster across PHASE-14 and PHASE-18

## Proposed New Phases

### PHASE-14 - Runtime Conformance, Deterministic Simulation, and Replay Oracle

- Objective: turn Aegis from an implemented runtime into a provably consistent runtime.
- Why it exists: the core runtime is built and now needs a measuring instrument.
- What it unlocks: safer refactors, upgrade rehearsals, benchmarkability, extension certification, and stronger product trust.
- Why it comes now: every later maturity step depends on a reliable oracle and simulator.
- Principal risks: simulator drift from real runtime behavior and over-engineering the lab before it proves value.
- Expected complexity: very high

### PHASE-15 - Upgrade Safety, Schema Evolution, and Disaster Recovery

- Objective: make version changes, migrations, rolling upgrades, restores, and standby promotion boring and evidence-backed.
- Why it exists: durable runtimes usually fail in production when upgrade semantics are fuzzy.
- What it unlocks: safe continuous delivery, stronger managed operation, and serious enterprise credibility.
- Why it comes now: PHASE-14 provides the proving ground needed to validate upgrade and restore behavior.
- Principal risks: skew edge cases, false confidence from incomplete drills, and silent replay breakage after schema evolution.
- Expected complexity: very high

### PHASE-16 - Fleet Scheduling, Isolation, and SLO-Driven Operability

- Objective: make Aegis predictable under load by formalizing resource models, placement policy, noisy-neighbor isolation, and overload behavior.
- Why it exists: many systems are correct in principle but operationally unstable under large-tenant pressure.
- What it unlocks: large deployments, cost-aware managed service operation, premium tenant tiers, and credible fleet-scale SLOs.
- Why it comes now: there is no point optimizing behavior at scale until replay and upgrade semantics are trusted.
- Principal risks: scheduler complexity, too many policy knobs, and accidental coupling between correctness and optimization.
- Expected complexity: very high

### PHASE-17 - Regional Topology, Fault Domains, and Session Mobility

- Objective: formalize fault domains, regional standby strategy, session evacuation, and region-aware placement while preserving the single-owner invariant.
- Why it exists: enterprise readiness is not the same thing as geographically mature control-plane design.
- What it unlocks: stronger disaster posture, regulated deployment options, and region-aware SLOs.
- Why it comes now: it depends on trusted replay, restore, and placement behavior.
- Principal risks: split-brain, stale approvals, artifact divergence, and runaway topology complexity.
- Expected complexity: extreme

### PHASE-18 - Certified Ecosystem, Governed Extensions, and Public Compatibility Leadership

- Objective: turn the extension surface into a certified, sandboxed, compatibility-governed ecosystem.
- Why it exists: extensibility becomes moat only when it is governed and testable.
- What it unlocks: safer adoption, partner ecosystem growth, and category leadership through public conformance.
- Why it comes now: certification is only credible after runtime guarantees and topology maturity exist.
- Principal risks: ecosystem sprawl, support burden, and backward-compatibility drag.
- Expected complexity: high

### PHASE-19 - Reference Adoption, Operator Drills, and Golden-Path Starter Kits

- Objective: turn the proof surfaces from PHASE-14 through PHASE-18 into repeatable first-adopter tracks.
- Why it exists: a state-of-the-art runtime still needs bounded rollout paths so adoption does not depend on the original authors.
- What it unlocks: safer onboarding, reproducible operator training, and clearer deployment entry points for serious adopters.
- Why it comes now: starter kits and rollout tracks are only credible after certification, regional evidence, fleet evidence, and release evidence already exist.
- Principal risks: drifting into tutorial prose, implying hidden defaults, and weakening runtime rigor for convenience.
- Expected complexity: medium

### PHASE-20 - Operational Lifecycle Governance, Rollout Waves, and Deprecation Discipline

- Objective: turn first adoption into a sustainable operating model through explicit accreditation, rollout, incident-review, and sunset surfaces.
- Why it exists: once serious adopters arrive, the next failure mode is process drift around who is accredited, how rollouts promote, how incidents are handed off, and how old surfaces retire.
- What it unlocks: bounded long-lived operations, clearer customer handoff, and safer change over time.
- Why it comes now: it depends on the committed evidence, adoption tracks, and certified ecosystem surfaces from PHASE-15 through PHASE-19.
- Principal risks: devolving into prose-heavy process docs or implying hidden authority outside runtime boundaries.
- Expected complexity: medium

## Detailed Task Graph

## PHASE-14 tasks

### P14-T01 - Define replay oracle and determinism taxonomy

- Goal: formalize what equivalent replay means across full replay, checkpoint-plus-tail replay, and historical replay.
- Dependencies: PHASE-02, PHASE-08
- Deliverables:
  - `docs/design-docs/replay-oracle.md`
  - `meta/determinism-classes.yaml`
  - `meta/replay-equivalence.yaml`
  - ADR for replay oracle and determinism policy
- Required schemas/contracts:
  - `schema/jsonschema/replay-oracle.schema.json`
  - `schema/jsonschema/determinism-classification.schema.json`
- Required tests/gates:
  - `tests/replay_oracle/`
  - `tests/phase-gates/phase-14-replay-equivalence.yaml`
- Acceptance criteria:
  - every event type and checkpoint field is classified as deterministic, captured-nondeterministic, or externally unknowable
  - replay from genesis and replay from checkpoint yield equivalent runtime truth for golden fixtures
  - historical replay never re-executes external side effects
- Anti-scope:
  - no theorem-proving detour
  - no claim of reconstructing uncaptured external world state

### P14-T02 - Build scenario DSL and deterministic simulation runner

- Goal: create a scenario language that can drive sessions, workers, faults, timers, approvals, and artifacts without live external systems.
- Dependencies: P14-T01
- Deliverables:
  - `docs/design-docs/simulation-lab.md`
  - `meta/fault-injection-matrix.yaml`
  - `meta/simulation-scenarios.yaml`
  - `tests/simulation/`
- Required schemas/contracts:
  - `schema/jsonschema/simulation-scenario.schema.json`
  - `schema/jsonschema/fault-injection-step.schema.json`
  - `schema/jsonschema/simulation-result.schema.json`
- Required tests/gates:
  - `tests/phase-gates/phase-14-simulation.yaml`
- Acceptance criteria:
  - a scenario can deterministically reproduce worker crash, node loss, approval timeout, duplicate callback, and browser instability
  - the runner emits a canonical timeline and expected terminal state
- Anti-scope:
  - no full browser emulator
  - no drift into general model-eval tooling

### P14-T03 - Build cross-language contract conformance suite

- Goal: prove Elixir, Python, and Rust all agree on envelopes, lifecycle edges, heartbeat semantics, errors, and token-bound execution metadata.
- Dependencies: P14-T01, PHASE-04, PHASE-07, PHASE-11
- Deliverables:
  - `docs/design-docs/contract-conformance.md`
  - `tests/conformance/`
  - golden fixture corpus
- Required tests/gates:
  - protobuf round-trip tests
  - schema validation tests
  - `tests/phase-gates/phase-14-contract-conformance.yaml`
- Acceptance criteria:
  - all supported languages pass the same golden fixtures
  - invalid fixtures fail with expected typed error classes
  - heartbeat, cancel, retry, and terminal callbacks behave consistently across languages
- Anti-scope:
  - no full SDK redesign
  - no marketplace work

### P14-T04 - Build replay differential harness across versions and failure paths

- Goal: compare replay, hydration, recovery, and final state across runtime versions and execution paths.
- Dependencies: P14-T01, P14-T02, P14-T03
- Deliverables:
  - `tests/replay_diff/`
  - `meta/replay-fixtures.yaml`
  - `docs/design-docs/replay-diffing.md`
- Required tests/gates:
  - `tests/phase-gates/phase-14-replay-diff.yaml`
- Acceptance criteria:
  - critical fixtures replay across the current and previous supported versions
  - any replay divergence emits a structured diff and blocks the gate
- Anti-scope:
  - no arbitrary historical version support
  - no silent auto-healing of diffs

### P14-T05 - Create benchmark corpus and correctness scorecards

- Goal: establish reproducible scorecards for correctness, replay cost, recovery time, and transport conformance.
- Dependencies: P14-T02, P14-T04
- Deliverables:
  - `benchmarks/`
  - `meta/benchmark-corpus.yaml`
  - `meta/performance-budgets.yaml`
  - generated scorecards under `docs/generated/`
- Required tests/gates:
  - `tests/benchmarks/`
  - `tests/phase-gates/phase-14-benchmark-scorecard.yaml`
- Acceptance criteria:
  - benchmark runs are reproducible from fixture manifests
  - regressions beyond configured budgets fail unless explicitly waived
- Anti-scope:
  - no vanity throughput work
  - no marketing-site detour

### P14-T06 - Ship developer simulation kit and fixture authoring flow

- Goal: make it cheap to add deterministic scenarios, replay fixtures, and fault cases.
- Dependencies: P14-T02, P14-T04
- Deliverables:
  - scaffold scripts
  - `docs/runbooks/author-simulation-fixture.md`
  - prompt pack updates
- Required tests/gates:
  - smoke test for fixture scaffolding
- Acceptance criteria:
  - a new simulation fixture can be scaffolded, validated, and run locally through one bounded workflow
- Anti-scope:
  - no low-code scenario builder
  - no GUI-first investment

## PHASE-15 tasks

### P15-T01 - Define compatibility matrix and version-skew policy

- Goal: explicitly define supported version windows across runtime, workers, schemas, checkpoints, policies, and extensions.
- Dependencies: PHASE-14
- Deliverables:
  - `docs/design-docs/upgrade-compatibility.md`
  - `meta/compatibility-matrix.yaml`
  - `meta/version-skew-rules.yaml`
  - ADR for version skew policy
- Required tests/gates:
  - validator ensuring every contract-bearing artifact declares compatibility status
- Acceptance criteria:
  - every runtime contract, checkpoint version, event payload version, and extension version appears in the compatibility matrix
  - unsupported skew combinations fail validation before runtime tests begin
- Anti-scope:
  - no promise of permanent backward compatibility
  - no ad hoc compatibility exceptions

### P15-T02 - Build event/checkpoint upcaster pipeline

- Goal: make historical data safely readable by newer runtime versions via explicit upcasters and migration manifests.
- Dependencies: P15-T01
- Deliverables:
  - `docs/design-docs/schema-evolution.md`
  - `meta/upcaster-manifests.yaml`
  - `tests/migrations/`
- Required schemas/contracts:
  - `schema/jsonschema/upcaster-manifest.schema.json`
- Required tests/gates:
  - migration replay tests
  - upcaster coverage validator
- Acceptance criteria:
  - supported prior versions can be loaded, upcast, and replayed into the current runtime
  - unsupported versions fail with typed quarantine or incompatibility reasons
- Anti-scope:
  - no default destructive rewriting of historical events
  - no hidden migration magic

### P15-T03 - Implement rolling upgrade and lease-safe drain/adopt protocol

- Goal: support mixed-version runtime clusters and worker pools during controlled upgrades.
- Dependencies: P15-T01, P15-T02
- Deliverables:
  - `docs/design-docs/rolling-upgrades.md`
  - `docs/runbooks/rolling-upgrade.md`
  - `meta/upgrade-strategies.yaml`
  - mixed-version adoption tests
- Required tests/gates:
  - `tests/upgrade_dr/`
  - `tests/phase-gates/phase-15-rolling-upgrade.yaml`
- Acceptance criteria:
  - a node can drain active sessions, transfer leases, and exit without duplicate side effects
  - mixed-version control-plane nodes preserve approvals, replay behavior, and suppression rules
- Anti-scope:
  - no active-active multi-writer design
  - no hidden topology redesign

### P15-T04 - Build backup, PITR, and restore-drill harness

- Goal: automate backup verification and restore drills for truth store, checkpoints, and artifact inventory reconciliation.
- Dependencies: P15-T02
- Deliverables:
  - `docs/design-docs/disaster-recovery.md`
  - `docs/runbooks/pitr-restore.md`
  - `meta/recovery-objectives.yaml`
  - restore drill scripts and fixtures
- Required tests/gates:
  - `tests/disaster_recovery/`
  - `tests/phase-gates/phase-15-restore-drill.yaml`
- Acceptance criteria:
  - restore drills reproduce valid control-plane state from backup plus replay tail within declared RTO/RPO profiles
  - integrity checks pass for event chain, checkpoint references, and artifact metadata inventory
- Anti-scope:
  - no cloud-vendor lock-in
  - no shortcuts that assume the backup exists and is valid

### P15-T05 - Add warm-standby topology and promotion evidence

- Goal: formalize an authoritative warm-standby profile and promotion procedure.
- Dependencies: P15-T03, P15-T04
- Deliverables:
  - `docs/design-docs/standby-topology.md`
  - `docs/runbooks/standby-promotion.md`
  - `meta/topology-profiles.yaml`
- Required tests/gates:
  - standby promotion drill
  - `tests/phase-gates/phase-15-standby-promotion.yaml`
- Acceptance criteria:
  - a standby environment can be promoted using documented fencing and restore procedures without violating the single-owner invariant
- Anti-scope:
  - no cross-region active-active control plane
  - no live session migration yet

### P15-T06 - Gate releases on compatibility and recovery evidence

- Goal: make upgrade and disaster recovery evidence release-blocking.
- Dependencies: P15-T01 through P15-T05
- Deliverables:
  - release gate docs
  - generated evidence bundles
  - CI/release workflow updates
- Required tests/gates:
  - `tests/phase-gates/phase-15-release-evidence.yaml`
- Acceptance criteria:
  - a release candidate cannot pass without green replay-diff, skew, rolling-upgrade, and restore-drill evidence
- Anti-scope:
  - no scope creep into external audit automation
  - no weakening gates for release velocity

## PHASE-16 tasks

### P16-T01 - Define capacity model, SLO profiles, and overload doctrine

- Goal: make system behavior under load explicit rather than emergent.
- Dependencies: PHASE-14, PHASE-15
- Deliverables:
  - `docs/design-docs/capacity-model.md`
  - `meta/slo-profiles.yaml`
  - `meta/performance-budgets.yaml`
  - `meta/load-shed-policies.yaml`
- Required tests/gates:
  - `tests/performance/`
  - `tests/phase-gates/phase-16-capacity-budgets.yaml`
- Acceptance criteria:
  - every critical path has explicit SLI/SLO, overload behavior, and protected budget
  - overload responses are policy-driven and validated in simulation and load tests
- Anti-scope:
  - no vanity dashboard sprint
  - no uncontrolled tuning before budgets are explicit

### P16-T02 - Implement session placement engine and pool taxonomy

- Goal: make session-owner placement and execution pool routing explainable, repeatable, and policy-driven.
- Dependencies: P16-T01
- Deliverables:
  - `docs/design-docs/placement-engine.md`
  - `meta/placement-policies.yaml`
  - ADR for placement and pool taxonomy
- Required schemas/contracts:
  - `schema/jsonschema/placement-decision.schema.json`
- Required tests/gates:
  - `tests/placement/`
  - `tests/phase-gates/phase-16-placement.yaml`
- Acceptance criteria:
  - identical inputs produce identical placement decisions
  - decisions are explainable by policy and compatible with tenant tier, fault domain, capability, and hotness constraints
- Anti-scope:
  - no ML scheduler
  - no cross-region session migration in this phase

### P16-T03 - Build adaptive admission control and load shedding

- Goal: protect correctness and premium paths during overload.
- Dependencies: P16-T01, P16-T02
- Deliverables:
  - `docs/design-docs/load-shedding.md`
  - `docs/runbooks/overload-response.md`
  - protected-class and shed-class tests
- Required tests/gates:
  - `tests/load_shedding/`
  - `tests/phase-gates/phase-16-overload.yaml`
- Acceptance criteria:
  - under synthetic overload, protected effectful actions and recovery flows retain budgeted service while lower-priority admissions are delayed or rejected by policy
- Anti-scope:
  - no hidden degradation
  - no dropping operator-critical events

### P16-T04 - Implement noisy-neighbor isolation and hot-tenant mitigation

- Goal: detect, attribute, and isolate pressure from misbehaving tenants or workflow classes.
- Dependencies: P16-T02, P16-T03
- Deliverables:
  - `docs/design-docs/isolation-profiles.md`
  - `meta/isolation-profiles.yaml`
  - tenant-pressure tests
- Required tests/gates:
  - `tests/noisy_neighbor/`
  - `tests/phase-gates/phase-16-isolation.yaml`
- Acceptance criteria:
  - the system can identify the causing tenant/workflow, apply isolation response, and preserve unaffected budgets
- Anti-scope:
  - no bespoke tenant code paths
  - no bypassing runtime invariants to preserve throughput

### P16-T05 - Formalize storage and transport scaling plan

- Goal: scale truth store, outbox, projections, and artifact indexes without diluting architecture.
- Dependencies: P16-T01
- Deliverables:
  - `docs/design-docs/data-plane-scaling.md`
  - ADR for Postgres/outbox scaling constraints and partitioning policy
  - storage growth fixtures
- Required tests/gates:
  - `tests/performance/storage_growth/`
  - `tests/phase-gates/phase-16-storage-transport.yaml`
- Acceptance criteria:
  - synthetic growth tests validate partitioning, retention, and projector behavior without breaking canonical truth semantics
- Anti-scope:
  - no replacement of Postgres as source of truth
  - no warehouse shortcut for control-plane truth

### P16-T06 - Add fleet forensics and operator evidence bundles

- Goal: upgrade operator surfaces from session inspection to fleet reasoning.
- Dependencies: P16-T01 through P16-T05
- Deliverables:
  - `docs/product-specs/fleet-triage.md`
  - `docs/runbooks/top-failure-clusters.md`
  - evidence-bundle export design
- Required schemas/contracts:
  - `schema/jsonschema/operator-evidence-bundle.schema.json`
- Required tests/gates:
  - `tests/operator_fleet/`
  - `tests/phase-gates/phase-16-fleet-triage.yaml`
- Acceptance criteria:
  - operators can compare sessions or cohorts, identify repeated failure signatures, export evidence bundles, and act using SLO-aware recommendations
- Anti-scope:
  - no AI operator-copilot detour
  - no summarization magic in place of evidence

## Repo-Ready Artifacts To Add

### Phase plans and work items

- `docs/exec-plans/active/PHASE-14-runtime-conformance-simulation.md`
- `docs/exec-plans/active/PHASE-15-upgrades-dr.md`
- `docs/exec-plans/active/PHASE-16-fleet-scheduling-isolation.md`
- `docs/exec-plans/active/PHASE-17-regional-topology.md`
- `docs/exec-plans/active/PHASE-18-certified-ecosystem.md`
- `docs/exec-plans/active/PHASE-19-reference-adoption-golden-paths.md`
- `docs/exec-plans/active/PHASE-20-operational-lifecycle-governance.md`
- matching `work-items/phase-14-*.yaml` through `work-items/phase-20-*.yaml`

### Machine-readable SSOT

- `meta/determinism-classes.yaml`
- `meta/replay-equivalence.yaml`
- `meta/fault-injection-matrix.yaml`
- `meta/simulation-scenarios.yaml`
- `meta/replay-fixtures.yaml`
- `meta/benchmark-corpus.yaml`
- `meta/compatibility-matrix.yaml`
- `meta/version-skew-rules.yaml`
- `meta/upcaster-manifests.yaml`
- `meta/recovery-objectives.yaml`
- `meta/upgrade-strategies.yaml`
- `meta/topology-profiles.yaml`
- `meta/slo-profiles.yaml`
- `meta/performance-budgets.yaml`
- `meta/load-shed-policies.yaml`
- `meta/placement-policies.yaml`
- `meta/isolation-profiles.yaml`
- `meta/extension-certification-levels.yaml`
- `meta/policy-bundle-profiles.yaml`
- `meta/public-benchmark-manifest.yaml`

### Schemas and contracts

- `schema/jsonschema/replay-oracle.schema.json`
- `schema/jsonschema/determinism-classification.schema.json`
- `schema/jsonschema/simulation-scenario.schema.json`
- `schema/jsonschema/fault-injection-step.schema.json`
- `schema/jsonschema/simulation-result.schema.json`
- `schema/jsonschema/conformance-report.schema.json`
- `schema/jsonschema/benchmark-run.schema.json`
- `schema/jsonschema/benchmark-scorecard.schema.json`
- `schema/jsonschema/upcaster-manifest.schema.json`
- `schema/jsonschema/recovery-objective.schema.json`
- `schema/jsonschema/placement-decision.schema.json`
- `schema/jsonschema/operator-evidence-bundle.schema.json`
- `schema/jsonschema/extension-certification-report.schema.json`
- `schema/jsonschema/policy-bundle-manifest.schema.json`

### Tests and phase gates

- `tests/replay_oracle/`
- `tests/simulation/`
- `tests/conformance/`
- `tests/replay_diff/`
- `tests/benchmarks/`
- `tests/migrations/`
- `tests/upgrade_dr/`
- `tests/disaster_recovery/`
- `tests/placement/`
- `tests/load_shedding/`
- `tests/noisy_neighbor/`
- `tests/operator_fleet/`
- `tests/regional_failover/`
- `tests/extensions_conformance/`
- `tests/sandbox_profiles/`
- `tests/phase-gates/phase-14-replay-equivalence.yaml`
- `tests/phase-gates/phase-14-simulation.yaml`
- `tests/phase-gates/phase-14-contract-conformance.yaml`
- `tests/phase-gates/phase-15-rolling-upgrade.yaml`
- `tests/phase-gates/phase-15-restore-drill.yaml`
- `tests/phase-gates/phase-15-release-evidence.yaml`
- `tests/phase-gates/phase-16-placement.yaml`
- `tests/phase-gates/phase-16-overload.yaml`
- `tests/phase-gates/phase-16-isolation.yaml`
- `tests/phase-gates/phase-17-regional-promotion.yaml`
- `tests/phase-gates/phase-18-extension-certification.yaml`

### Runbooks and ADRs

- `docs/runbooks/author-simulation-fixture.md`
- `docs/runbooks/rolling-upgrade.md`
- `docs/runbooks/pitr-restore.md`
- `docs/runbooks/standby-promotion.md`
- `docs/runbooks/overload-response.md`
- `docs/runbooks/hot-tenant-isolation.md`
- `docs/runbooks/regional-evacuation.md`
- `docs/runbooks/revoking-extension.md`
- `docs/runbooks/policy-bundle-rollback.md`
- ADRs for replay oracle, simulation DSL boundary, benchmark philosophy, compatibility windows, upcaster policy, rolling upgrades, placement, load shedding, regional topology, and extension certification

## Priority Recommendation

### Single most important next phase

PHASE-14 is the highest-leverage next move.
Without it, Aegis risks becoming a very strong runtime that still cannot prove its own correctness envelope under change.

### Top five highest-leverage tasks

- P14-T01 - define replay oracle and determinism taxonomy
- P14-T02 - build scenario DSL and deterministic simulation runner
- P15-T03 - implement rolling upgrade and lease-safe drain/adopt protocol
- P15-T04 - build backup, PITR, and restore-drill harness
- P16-T02 - implement session placement engine and pool taxonomy

### Biggest architectural risk if the project stops now

The project risks becoming feature-complete but not proof-complete.
It would be strong enough to run serious workloads, but not strong enough to establish lasting category leadership because it would still lack:

- replay equivalence rigor
- disciplined upgrade semantics
- practiced disaster recovery
- explicit scale behavior
- benchmark-backed authority

### Biggest temptation to resist

Do not broaden the surface area before hardening the runtime core.
The most dangerous distractions are:

- more modalities for their own sake
- more connectors without certification
- more UI polish without fleet-scale operator rigor
- generic autonomy features
- vertical app work that dilutes the runtime thesis

The popular distraction is breadth.
The correct move is deeper rigor.

## Final Summary

### Proposed PHASE-14+ roadmap

- PHASE-14: runtime conformance, deterministic simulation, replay oracle, benchmark corpus
- PHASE-15: upgrade safety, schema evolution, rolling upgrades, PITR/restore, standby promotion
- PHASE-16: fleet scheduling, placement, load shedding, noisy-neighbor isolation, fleet forensics
- PHASE-17: regional topology, fault domains, standby/evacuation semantics
- PHASE-18: certified ecosystem, governed extensions, policy bundles, public compatibility leadership
- PHASE-19: reference adoption, operator drills, and golden-path starter kits
- PHASE-20: operational lifecycle governance, rollout waves, incident review, and deprecation discipline

### What would make Aegis feel state of the art

Aegis will feel state-of-the-art when it becomes powerful **and** provable:

- replay is oracle-backed
- failures are reproducible in simulation
- upgrades are rehearsed and gated
- restore is drilled and evidenced
- load behavior is predictable
- regional topology is explicit
- extensions are certified, sandboxed, and benchmarked
- the project publishes a conformance and benchmark story others must measure themselves against

### What would make it merely feature-rich

Aegis becomes merely feature-rich if future work focuses on:

- more connectors
- more UI surfaces
- more modalities
- cosmetic console polish
- marketplace-style ecosystem breadth
- more agentic behavior

without first building:

- simulation
- replay oracle
- upgrade discipline
- DR drills
- scale isolation
- regional fault-domain semantics

That path produces a big system, but not a great one.
