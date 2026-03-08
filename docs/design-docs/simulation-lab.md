# Simulation Lab

## Purpose

The PHASE-14 simulation lab gives Aegis a deterministic way to exercise replay,
recovery, approvals, timers, artifacts, and injected faults without requiring live
external systems.

It is not a browser emulator and it is not a model-evaluation framework.
It is a controlled runtime lab for proving that failure handling and replay semantics
remain stable under change.

## Goals

- express runtime scenarios as machine-checkable fixtures
- inject canonical fault classes in a deterministic way
- emit canonical timeline evidence and expected terminal state
- keep scenario authoring cheap enough to become part of normal repo work

## Scenario model

The canonical scenario DSL lives in `schema/jsonschema/simulation-scenario.schema.json`.
Every scenario defines:

- a stable `id`
- a deterministic `seed`
- a bounded set of `steps`
- an `expected_terminal_state`
- the invariants it intends to prove

The initial step taxonomy is deliberately small:

- `command`
- `approval`
- `fault_injection`
- `timer`
- `artifact_capture`

This is enough to model the runtime concerns PHASE-14 cares about without turning
the simulation lab into a second orchestration system.

## Fault model

The canonical supported fault set lives in `meta/fault-injection-matrix.yaml`.
The initial supported matrix covers:

- worker crash
- node loss
- approval timeout
- duplicate callback
- browser instability

Each supported fault declares:

- target scope
- deterministic replay expectations
- the expected runtime response class

## Result model

The canonical simulation result contract lives in
`schema/jsonschema/simulation-result.schema.json`.

Every simulation run emits:

- a scenario identifier
- the seed used
- the canonical emitted event list
- the applied fault list
- the terminal state summary
- a deterministic result signature

The signature exists so fixture authoring and CI can detect unintended drift.

## Determinism rules

- The runner never calls browsers, model providers, or external APIs.
- The same fixture and seed must always produce the same result payload.
- Fault injection is declarative and scenario-driven.
- The runner is allowed to model runtime outcomes, not external world state.

## Relationship to replay oracle

The simulation lab depends on the replay oracle defined in
`docs/design-docs/replay-oracle.md`.
Simulation outputs are useful only if they preserve the same truth boundaries:

- deterministic state is recomputed
- captured nondeterministic evidence is replayed from recorded artifacts
- externally unknowable state remains explicit uncertainty

## Initial acceptance boundary

The PHASE-14 simulation lab is considered present when:

- the scenario DSL is machine-checkable
- canonical fault fixtures exist for the initial matrix
- the runner emits deterministic results
- the phase gate references real docs, schemas, fixtures, and tests

## Non-goals

- full browser emulation
- synthetic model quality scoring
- GUI scenario builders
- replacing the real runtime with the simulation lab
