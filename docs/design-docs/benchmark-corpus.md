# Benchmark Corpus And Correctness Scorecards

## Purpose

PHASE-14 benchmark scorecards give Aegis a reproducible way to measure whether the
replay and simulation lab is drifting in ways that should block further runtime
changes.

This phase does **not** claim to measure real fleet throughput.
It measures deterministic fixture cost and correctness.

## Why this exists

Replay and simulation are valuable, but they are still easy to treat as qualitative
proof.
The benchmark corpus turns them into a repeatable regression surface with explicit
budgets and a generated scorecard artifact.

## Inputs

The scorecard is generated from:

- `meta/benchmark-corpus.yaml`
- `meta/performance-budgets.yaml`
- `meta/replay-fixtures.yaml`
- deterministic simulation scenarios under `tests/simulation/fixtures/`

## Cost model

PHASE-14 uses a **fixture-derived** cost model.
It is intentionally simple and deterministic:

- emitted event count contributes to estimated replay cost
- injected fault count contributes to recovery complexity cost
- artifact registrations contribute to evidence-handling cost
- replay comparison mode contributes to diffing overhead

This produces a stable `estimated_runtime_ms` number for regression gating.

The number is **not** a wall-clock promise.
It is a deterministic budget signal that helps catch accidental complexity growth
before later scale phases add live load and placement work.

## Correctness scoring

Each benchmark case also carries a correctness score.
The initial score is derived from replay-diff results:

- current-baseline signature match
- previous-supported equivalence
- replay-diff verdict

If those regress, the scorecard fails regardless of the deterministic cost estimate.

## Generated artifact

The runner writes a canonical scorecard to:

- `docs/generated/phase-14-benchmark-scorecard.json`

This checked-in artifact exists so CI and local validation can detect drift between
the committed corpus and the generated scorecard.

## Non-goals

- public marketing benchmarks
- live cloud throughput claims
- latency numbers from unstable developer machines
- replacing later fleet-scale performance work
