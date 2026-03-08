# Enterprise control matrix

This document defines the PHASE-13 enterprise control surface.

## Goal

Make enterprise claims traceable to concrete controls, machine-readable artifacts, and operator runbooks.

## Canonical matrix

The machine-readable control catalog lives in `meta/enterprise-control-matrix.yaml`.

The dedicated-deployment evidence bundle lives in `meta/dedicated-tenant-evidence.yaml`.

## Control map

| Control area | Enterprise requirement | Evidence sources |
|---|---|---|
| Identity and scoped authz | Enterprise auth uses OIDC/SAML with tenant/workspace scoped RBAC/ABAC and bounded audit-export roles. | `meta/rbac-roles.yaml`, `meta/abac-attributes.yaml`, `docs/operations/security.md`, `docs/design-docs/audit-export-redaction.md` |
| Dedicated isolation boundary | Tier C dedicated deployment uses dedicated control plane, worker pools, and dedicated object store. | `meta/dedicated-deployment-profile.yaml`, `meta/deployment-flavors.yaml`, `docs/design-docs/dedicated-deployment-isolation.md` |
| Key isolation and secrets | Dedicated KMS namespace and external secret manager custody keep tenant keys separated. | `meta/dedicated-deployment-profile.yaml`, `docs/operations/security.md`, `docs/runbooks/dedicated-key-isolation.md` |
| Residency and artifact controls | Dedicated deployment pins database, object-store, and key region while keeping short-lived signed URL access. | `meta/dedicated-tenant-evidence.yaml`, `meta/dedicated-deployment-profile.yaml`, `docs/design-docs/dedicated-deployment-isolation.md` |
| Audit, evidence, and replay | Audit export packages timeline hashes, approvals, policy decisions, and artifact metadata without bypassing redaction state. | `meta/audit-export-policy.yaml`, `docs/design-docs/audit-export-redaction.md`, `docs/design-docs/security-governance.md` |
| Redaction and retention | Retention classes, archive restore, and redaction completion are explicit bounded policies. | `meta/retention-slo-policy.yaml`, `docs/design-docs/retention-and-slo-policy.md`, `docs/operations/reliability.md` |
| Change control and release gate | Enterprise acceptance checklist and readiness gate must pass before dedicated deployment claims. | `meta/enterprise-acceptance-checklist.yaml`, `tests/phase-gates/enterprise-readiness.yaml`, `meta/dedicated-tenant-evidence.yaml` |
| Runbooks and operator recovery | Enterprise failures map to explicit runbooks and operator-visible degraded paths. | `meta/failure-runbooks.yaml`, `docs/runbooks/audit-export-backlog.md`, `docs/runbooks/dedicated-key-isolation.md`, `docs/runbooks/retention-backlog.md` |

## Phase-09 continuity

Enterprise hardening builds on the Phase 09 security foundation rather than replacing it.
That continuity includes:

- quota and admission control remain part of the enterprise trust story
- tiered isolation routing remains visible in dispatch metadata and operator evidence
- audit, evidence, and replay remain the forensic backbone for enterprise recovery

## Enterprise follow-through

Phase 13 does not claim every certification.
It does make dedicated deployment, key isolation, audit export, retention, and operator recovery implementation-grade instead of aspirational.
