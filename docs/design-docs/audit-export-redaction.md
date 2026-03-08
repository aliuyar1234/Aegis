# Audit export and redaction

This document defines the PHASE-13 audit-export path for enterprise packaging.

## Goal

Make audit export implementation-grade without turning export bundles into a hidden second source of truth.

## Canonical policy artifact

The machine-readable policy lives in `meta/audit-export-policy.yaml`.

## Export scope

Enterprise audit export includes:

- session timeline events with integrity hashes
- approval and policy decision trail
- operator interventions
- artifact metadata

Enterprise audit export does not move raw artifact blobs through the control plane.
Artifact evidence is rehydrated through signed URLs only.

## Identity and authorization

- human export access is gated by OIDC or SAML-backed roles
- machine delivery uses workload identity or mTLS
- exports remain tenant and workspace scoped
- `auditor` and `platform_admin` are the bounded export roles at this phase

## Redaction rules

- every exported artifact record must preserve `redaction_state`
- raw secret material is forbidden in export bundles
- PII export requires explicit policy allowance
- redacted records stay visible as redacted stubs rather than disappearing silently

## Failure handling

Audit export failure must become operator-visible backlog, not silent drift.

Use `docs/runbooks/audit-export-backlog.md` when export delivery, export staging, or signed-url evidence packaging degrades.
