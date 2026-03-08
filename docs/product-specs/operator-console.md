# Operator console product spec

## Purpose

The operator console is the human control surface for Aegis. It is part of the runtime.

## Stable data source

The console reads from:
- `schema/proto/aegis/runtime/v1/operator.proto`
- `schema/jsonschema/operator-session-view.schema.json`

## Required screens

### Session fleet
- session id and tenant/workspace context
- owner node and lease epoch
- phase / control mode / health
- wait reason
- pending approvals
- degraded/quarantined markers

### Session detail
- timeline
- current state summary
- deadlines
- in-flight actions
- latest checkpoint
- current browser artifacts
- operator controls

### Replay
- timeline scrubber
- artifact playback
- checkpoint markers
- approvals and intervention overlays

### Approvals queue
- exact action request
- risk class
- action hash
- expiry
- evidence artifacts

## Anti-patterns

- UI-only state transitions
- vague approval copy
- hidden uncertainty
- requiring operators to infer owner or lease state from logs
