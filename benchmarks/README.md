# Benchmarks

This directory documents the benchmark surface for Aegis Runtime.

PHASE-14 intentionally uses a deterministic, fixture-derived benchmark corpus rather
than live wall-clock measurements.
The goal is to make replay and simulation regressions reproducible and gateable
before later phases add scale and throughput benchmarking.

The canonical benchmark inputs live in:

- `meta/benchmark-corpus.yaml`
- `meta/performance-budgets.yaml`

The canonical generated scorecard lives in:

- `docs/generated/phase-14-benchmark-scorecard.json`
