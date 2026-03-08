# Media session extensions

This document defines the future session-state additions required for voice/media work.

## Goal

Make future media sessions legible without breaking the current session-first runtime model.

## Extension areas

The future media extension adds bounded state for:

- `media_mode`
- QoS state and degradation reason
- capacity isolation and reservation posture
- active sidecars
- recording state and consent state
- operator handoff requirement
- replay boundary

The machine-checkable schema is `schema/jsonschema/media-session-extension.schema.json`.

The sample fixture is `tests/media/fixtures/sample-media-session-extension.yaml`.

## Rules

- media session extensions augment the session; they do not replace it
- raw packet buffers, codec state, and low-level transport internals stay out of checkpoints
- degraded QoS must be explicit, not inferred from logs
- operator handoff requirement must be explicit, not UI-only
- replay must stay artifact- and transcript-based instead of packet-based

## Recording state

Recording remains bounded by:

- explicit mode
- explicit consent state
- explicit artifact kind

This keeps future recording work aligned with existing approval, artifact, and retention boundaries.

## Capacity isolation

Media sessions must carry an explicit pool class so future admission control can distinguish:

- shared media pools
- tenant-isolated media pools
- dedicated media pools

This preserves the Phase 09 isolation story when media arrives later.
