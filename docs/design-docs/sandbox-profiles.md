# Sandbox profiles

This document defines the PHASE-18 sandbox posture for extensions.

## Goal

Make extension isolation explicit enough that connector admission is bounded by policy instead of reviewer intuition.

## Profile dimensions

Every sandbox profile constrains:

- allowed extension kinds
- allowed SDK languages
- allowed network modes
- maximum secret count
- whether MCP is permitted
- whether artifact outputs are mandatory
- which policy bundle governs the profile

The machine-readable source is `meta/sandbox-profiles.yaml`.

## Why profiles exist

Compatibility ranges alone do not control extension risk.
Sandbox profiles are the operating boundary between declarative extension manifests and runtime admission.

They are meant to answer:

- can this pack reach the network?
- how many secrets may it receive?
- is it an artifact-only processor or a connector?
- is an MCP edge adapter allowed here?
- which policy bundle explains the governance posture?

## Profile classes

- `restricted-artifact` for artifact processors with no network access
- `partner-reviewed` for bounded tool connectors with allowlisted egress
- `edge-adapter` for MCP adapters that stay on the external-tool edge

These classes are small on purpose.
Adding more profiles is slower than reusing one because every new profile expands the support surface.

## Assignment discipline

Sandbox posture is attached per extension manifest, not guessed from the pack name.
That allows mixed packs to remain reviewable while keeping each manifest bound to an explicit isolation posture.
