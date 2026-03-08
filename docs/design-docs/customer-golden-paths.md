# Customer golden paths

This document defines the canonical customer launch workflows for Aegis.

## Why this exists

Starter kits and adoption tracks are useful, but customer readiness requires tighter
proof: a reader must be able to point to the exact workflows that demonstrate the
runtime thesis under launch conditions.

## Required launch paths

Aegis launch readiness requires two bounded paths:

- one read-heavy browser-backed service operation
- one approval-gated browser write operation with replay and operator intervention

Both paths must stay anchored to committed starter kits, deployment tracks, runbooks,
and evidence bundles.

## Constraints

- do not invent launch workflows outside committed starter kits
- do not present a write path without explicit approval and intervention surfaces
- do not call a workflow launch-ready if its evidence path is missing
