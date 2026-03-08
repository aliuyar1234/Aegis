# Public compatibility leadership

This document defines the PHASE-18 public-facing compatibility surface for certified extension packs.

## Goal

Publish extension compatibility in a way that strengthens trust without implying that extensions can bypass runtime guarantees.

## Publication rules

Public tracks are allowed only when they are backed by:

- a certified extension pack
- explicit sandbox-profile coverage
- an explicit governing policy bundle
- the committed phase-14 benchmark scorecard

The machine-readable source is `meta/public-benchmark-manifest.yaml`.

## What public publication means

Public listing is a bounded statement that:

- the pack validated against the supported extension contract
- the pack maps to explicit sandbox posture
- the pack belongs to an explicit governance bundle
- the pack is presented alongside committed benchmark evidence

It does **not** mean:

- the extension can write canonical runtime state
- the extension can emit runtime events directly
- the extension can bypass policy or approvals
- the extension is promised indefinite compatibility

## Benchmark-backed tracks

The public compatibility surface reuses the committed benchmark scorecard instead of inventing a parallel marketing metric.
This keeps ecosystem claims tied to the same replay and recovery rigor used for the core runtime.
