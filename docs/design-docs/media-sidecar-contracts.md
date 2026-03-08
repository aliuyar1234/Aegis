# Media sidecar contracts

This document defines the future Rust sidecar boundary for voice/media work in Aegis.

## Why sidecars exist

Media, protocol, and recording hot paths do not belong on BEAM schedulers.

The sidecar boundary keeps:

- packet handling
- codec work
- protocol bridging
- recording segmentation

out of the Elixir control plane while preserving session ownership, replay, and policy boundaries.

## Stable sidecar kinds

The Phase 11 contract stub covers three future sidecars:

- `media_gateway` for realtime media transport and jitter-buffer work
- `recorder` for bounded recording segmentation and upload handoff
- `protocol_bridge` for SIP/WebRTC or other protocol adaptation

The machine-checkable catalog is `schema/jsonschema/media-sidecar-catalog.schema.json`.

The sample fixture is `tests/media/fixtures/sample-media-sidecars.yaml`.

## Ownership rules

- Elixir remains the session owner
- sidecars do not own leases
- sidecars do not write canonical runtime tables directly
- sidecars do not emit runtime events directly
- sidecar results return through normal worker-style acceptance/progress/completion paths

## Replay rules

Replay does not consume raw packets as truth.

Replay for future media sessions must reconstruct from:

- timeline events
- transcripts
- recording manifests
- artifact references

Raw packet streams may exist transiently in sidecars, but they are not canonical replay inputs.

## Artifact rules

- recording artifacts still register through the shared artifact metadata path
- signed upload remains mandatory
- retention classes must be explicit per artifact kind
- recorder sidecars may produce segments and manifests, but not hidden storage side channels

## Capacity and degradation

Every sidecar contract declares:

- pool class
- maximum streams per sidecar
- degradation signal

That keeps capacity isolation and degraded-mode behavior explicit before live media ships.

## Anti-patterns

- turning the sidecar into a second runtime owner
- treating protocol messages as canonical session state
- storing packet buffers in control-plane checkpoints
- letting media sidecars bypass policy or artifact retention rules
