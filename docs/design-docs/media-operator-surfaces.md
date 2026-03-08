# Media operator surfaces

This document defines the future operator-console deltas for voice/media sessions.

## Goal

Show the minimum additional state operators need for media sessions without inventing a second operator product.

## Future fleet deltas

Fleet rows for media sessions must surface:

- media mode
- QoS state and degradation reason
- media capacity pool
- handoff-required marker
- runbook link for media QoS degradation

## Future session-detail deltas

Session detail for media sessions must surface:

- active sidecars and their health
- QoS state and degradation reason
- recording mode and latest recording artifact
- whether operator handoff is required
- recommended runbooks

## Future replay deltas

Replay for media sessions must use:

- transcripts
- recording manifests
- artifact references
- timeline events

Replay must not pretend to be a raw packet scrubber.

## Operator actions

Phase 11 does not ship live telephony controls.

The bounded future delta is only:

- visibility into degraded QoS
- visibility into recording status
- explicit handoff recommendation
- runbook-driven recovery guidance

The machine-checkable view schema is `schema/jsonschema/operator-media-session-view.schema.json`.

The sample fixture is `tests/media/fixtures/sample-operator-media-session-view.yaml`.
