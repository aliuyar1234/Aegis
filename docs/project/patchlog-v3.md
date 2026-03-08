# Patchlog V3

This file summarizes the v3 hardening pass after the v2 audit.

## Why v3 exists

v2 was materially improved, but a fresh audit still found a few places where Codex could be forced to guess:
- transport topology declared runtime heartbeats without a matching runtime contract message;
- cancel-path consumer coverage was implicit instead of explicit;
- phase gates were machine-readable but still too loose to serve as strong execution gates;
- checkpoint and browser-fixture schemas were still typed too weakly in the most failure-sensitive areas;
- the handoff bundle still shipped cache/noise artifacts that do not belong in a clean SSOT repository.

## Major v3 fixes

- Added `ActionHeartbeat` to the runtime worker contract and wired it into transport topology.
- Made dispatch/cancel consumer coverage explicit in `schema/transport-topology.yaml` and local NATS bootstrap.
- Added `schema/jsonschema/transport-topology.schema.json` and validated topology structurally.
- Added `schema/jsonschema/phase-gate.schema.json` and strengthened all phase-gate YAML files.
- Upgraded `scripts/run_phase_gate.py` from a loose reference checker into a schema-aware gate validator with phase/acceptance consistency checks.
- Strengthened the checkpoint schema with typed nested definitions for action ledger, approvals, deadlines, child agents, browser handles, and summary capsule.
- Strengthened browser workflow fixtures and schema so mutation safety and uncertainty handling are more explicit.
- Strengthened repo/schema validators to check current-phase starting sequence, stream/subject/message consistency, and cache/noise exclusion.
- Cleaned repository caches and other non-SSOT artifacts from the bundle.
- Added clarifying documentation for runtime heartbeats, cancel semantics, and Elixir contract consumption strategy.

## Tradeoffs

- Local schema validation still falls back to structural proto checks when `buf` is unavailable locally. CI remains the authoritative `buf lint` / generation environment.
- Phase gates remain repository-level execution contracts rather than a full end-to-end runner against a live implementation. The specs are now typed and much stricter, but the running product still has to make them pass.
