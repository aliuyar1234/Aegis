# Media topology

This document supports PHASE-11.

## Purpose

Define the future voice/media data plane without changing Aegis's core thesis.

## Core rules

- media packets and codecs stay in Rust sidecars
- media artifacts register through the same artifact metadata path
- session ownership and replay remain in the Elixir control plane
- degraded QoS must surface as explicit runtime state and runbooks

## Future sidecar chain

The bounded future chain is:

1. `protocol_bridge`
2. `media_gateway`
3. `recorder`

This chain is captured in `tests/media/fixtures/sample-media-topology.yaml`.

## Transport policy

Future media ingress may use:

- WebRTC
- SIP
- RTMP where appropriate for ingest-only use cases

Transport termination stays in Rust sidecars. The control plane sees normalized session-scoped outcomes, not raw transport control.

## Recording and artifact policy

- recorder sidecars emit recording segments and recording manifests
- transcripts remain first-class replay evidence
- signed upload remains required for media artifacts
- retention class must stay explicit per artifact kind

## QoS degradation policy

Future media sessions must make these degradation classes explicit:

- `healthy`
- `degraded`
- `handoff_required`
- `paused_for_backpressure`

Admission and recording responses must be explicit rather than implicit. The sample topology fixture currently models:

- `require_operator_handoff` for admission response
- `artifact_only_fallback` for recording response

## Capacity isolation

Media topology must remain compatible with:

- shared media pools
- tenant-isolated media pools
- dedicated media pools

This avoids forcing a separate isolation story just because the data plane is realtime.
