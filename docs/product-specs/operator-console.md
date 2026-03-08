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

## Future Phase-11 media deltas

Future voice/media sessions add bounded console deltas rather than a separate console:

- QoS state and degradation reason on fleet/detail surfaces
- media sidecar health and capacity-pool visibility
- recording status and latest media artifact refs
- explicit handoff-required state and media-specific runbook links

The Phase 11 design SSOT is `docs/design-docs/media-operator-surfaces.md`.

## Future Phase-13 enterprise deltas

Future enterprise packaging adds bounded console deltas rather than a new control product:

- audit export status and backlog visibility for bounded audit roles
- dedicated deployment and key-isolation status markers
- retention and archive backlog indicators
- enterprise-specific runbook links for audit export, key isolation, and retention recovery

## Future Phase-16 fleet operability deltas

Future fleet operability work extends the console with bounded cohort reasoning rather
than replacing session detail and replay:

- fleet triage by shared failure signature
- placement and isolation drift markers
- bounded evidence-bundle export for operator handoff
- runbook-linked cohort summaries for overload, hot-tenant pressure, and storage lag

The Phase 16 design SSOT is `docs/product-specs/fleet-triage.md`.

## Future Phase-17 regional deltas

Future regional-topology work adds bounded regional context rather than a separate
operator product:

- authoritative region and standby-region markers on fleet and detail surfaces
- fault-domain and evacuation-state markers for affected cohorts
- bounded regional evidence-bundle export for failover drills
- runbook links for regional evacuation and regional promotion

The Phase 17 design SSOT is `docs/design-docs/regional-topology.md`.

## Anti-patterns

- UI-only state transitions
- shadow operator control paths that bypass runtime events
- vague approval copy
- hidden uncertainty
- replay reconstructed from browser memory instead of recorded events and artifacts
- requiring operators to infer owner or lease state from logs
