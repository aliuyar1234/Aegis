# Replay Diffing

## Purpose

Replay diffing compares replay outcomes across supported baselines and failure paths.
Its job is not to "fix" differences.
Its job is to make divergence visible, structured, and gateable.

## Why this exists

Replay correctness is stronger than "replay runs without crashing."
Aegis needs a way to compare:

- full replay expectations
- checkpoint-tail replay expectations
- supported previous baseline expectations

against the current runtime result for a fixture.

## Fixture model

The canonical replay-diff fixture registry lives in `meta/replay-fixtures.yaml`.
Each fixture references:

- a deterministic scenario source
- the current supported baseline
- the previous supported baseline
- the dimensions that must remain equivalent

The initial harness intentionally builds on the PHASE-14 simulation lab so replay
fixtures stay deterministic and cheap to run.

## Diff semantics

The current runtime result is compared against:

- the current baseline using exact deterministic signature equality
- the previous supported baseline using replay-equivalence dimensions

The previous baseline is allowed to differ in irrelevant observational detail, but it
may not differ in:

- terminal session truth
- event type sequence
- uncertainty surface
- replay-equivalent verdict

## Failure policy

If a diff fails, the harness emits a structured result and the gate blocks.
Aegis must not silently normalize or auto-heal replay divergence in this phase.

## Non-goals

- unlimited historical version support
- semantic diffing for arbitrary old runtimes
- hidden compatibility exceptions
