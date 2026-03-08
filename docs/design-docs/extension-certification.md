# Extension certification

This document defines the PHASE-18 certification surface for third-party extension packs.

## Goal

Admit extensions through explicit certification levels instead of one-off judgment calls.

## Certification levels

- `reviewed` means schemas, compatibility ranges, and sandbox mappings validate, but the pack is not listed publicly.
- `verified` means the pack has bounded governance and sandbox evidence and may appear on bounded compatibility surfaces.
- `certified` means the pack is reviewable, sandboxed, benchmark-backed, and eligible for publication under the public compatibility policy.

The machine-readable source of truth is `meta/extension-certification-levels.yaml`.

## Signed compatibility-report shape

Certification reports are structured outputs with:

- candidate pack identity
- target certification level
- discovered extension kinds
- required sandbox-profile coverage
- governing policy bundle
- public track identifier
- signature envelope with signing profile, signer role, and deterministic digest

The signature is a bounded compatibility attestation for the pack inputs.
It does not authorize the pack to bypass policy, approvals, or outbox semantics.

## Candidate-pack discipline

Certification is pack-oriented, not manifest-oriented.
Every candidate pack must point at:

- a committed extension-pack manifest
- committed member manifests
- explicit sandbox profiles
- an explicit policy bundle
- a public compatibility track if public listing is requested

This keeps certification tied to reviewable artifacts instead of mutable partner claims.

## Revocation and recertification

Certification is not permanent.
The program defines:

- revocation SLA
- required recertification cadence
- rollback linkage through `docs/runbooks/revoking-extension.md`

If sandbox posture, compatibility ranges, or governance inputs drift, certification is revoked until the pack is re-evaluated.
