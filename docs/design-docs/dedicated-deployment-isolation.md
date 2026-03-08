# Dedicated deployment isolation

This document defines the Tier C dedicated deployment path for PHASE-13.

## Goal

Describe how dedicated deployment changes packaging and isolation without changing the runtime thesis.

## Canonical profile

The machine-readable deployment profile lives in `meta/dedicated-deployment-profile.yaml`.

The evidence bundle lives in `meta/dedicated-tenant-evidence.yaml`.

## Dedicated deployment boundary

Tier C dedicated deployment means:

- dedicated control plane per tenant
- dedicated database/control-plane boundary
- dedicated worker pools and browser pools
- tenant-scoped media/protocol sidecars
- dedicated object-store boundary

It does not mean a separate event model, separate policy language, or alternate replay semantics.

## Key isolation

- dedicated deployment uses a dedicated KMS namespace
- artifact encryption uses a per-tenant wrapping key
- runtime secrets come from an external secret manager
- key rotation happens in a change window rather than opportunistically

## Data residency hooks

- database region pin must be explicit
- object-store region pin must be explicit
- key region pin must be explicit
- cross-region failover requires operator approval

## Network and access controls

- private connectivity is required by default
- ingress is bounded to private link, site-to-site VPN, or allowlisted public ingress
- egress stays on an explicit allowlist
- break-glass access is limited to bounded platform and security roles

## Runbook consequence

Key-isolation or residency drift is an operational incident, not an implementation detail.

Use `docs/runbooks/dedicated-key-isolation.md` for rotation, preflight, and containment guidance.
