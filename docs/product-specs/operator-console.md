# Operator console product spec

## Purpose

The operator console is the human control surface for Aegis. It is part of the runtime.

## Current implementation state

This document reflects the committed `PHASE-06` implementation.

Phase 06 ships:
- fleet inspection with bounded filters, system health, and runbook links
- session detail with approvals, artifacts, checkpoints, summaries, and intervention controls
- replay/timeline scrubber plus artifact inspection
- operator intervention actions represented as runtime events

Phase 06 does not ship a standalone approvals queue yet. Approval waits are surfaced through fleet, detail, and replay views instead of a separate screen.

## Stable data sources and boundaries

The stable query/control boundary is `Aegis.Gateway.OperatorConsole`.

Console reads come from:
- `schema/proto/aegis/runtime/v1/operator.proto`
- `schema/jsonschema/operator-session-view.schema.json`
- `Aegis.Events.historical_replay/1`
- `Aegis.Events.replay_at/2`
- checkpoint metadata and recorded artifact metadata

Operator controls must dispatch through the runtime and land as timeline events. There is no UI-only control path.

## Required screens

### Session fleet
- session id and tenant/workspace context
- owner node and lease epoch
- phase / control mode / health
- wait reason
- pending approvals
- degraded/quarantined markers
- system health summary with session counts and worker-fleet capacity/status
- bounded filters for tenant, workspace, session id, health, wait reason, approvals, and search query
- fleet-level runbook links for degraded-system and transport triage

### Session detail
- stable session snapshot plus current state summary
- summary capsule including operator notes
- deadlines
- approvals and in-flight actions
- latest checkpoint
- checkpoint history
- current browser artifacts with registration sequence/timestamp
- browser handle and child-agent summaries
- operator controls:
  `join`, `add_note`, `pause`, `abort`, `take_control`, `return_control`
- runbook links for recovery, artifact issues, operator intervention, and approval waits

### Replay
- timeline scrubber
- selected historical state at a chosen `seq_no`
- selected checkpoint at the scrubbed position
- artifact inspection by `artifact_id`
- checkpoint markers
- approvals, artifact, operator, wait, recovery, and health overlays
- scrubbed state must come from recorded events plus checkpoints, not browser memory
- replay-level runbook links for recovery-oriented investigation

## Deferred surfaces

- standalone approvals queue
- policy decision and dangerous-action surfaces
- effectful mutation controls

## Anti-patterns

- UI-only state transitions
- shadow operator control paths that bypass runtime events
- vague approval copy
- hidden uncertainty
- replay reconstructed from browser memory instead of recorded events and artifacts
- requiring operators to infer owner or lease state from logs
