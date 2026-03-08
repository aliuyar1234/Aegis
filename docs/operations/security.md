# Security

Aegis has to earn trust at runtime. Security, governance, and policy are part of the product.

## Machine-readable sources

- roles: `meta/rbac-roles.yaml`
- attributes: `meta/abac-attributes.yaml`
- dangerous actions: `meta/dangerous-action-classes.yaml`
- capability-token claims: `schema/jsonschema/capability-token-claims.schema.json`
- approval requests: `schema/jsonschema/approval-request.schema.json`
- operator session view: `schema/jsonschema/operator-session-view.schema.json`
- enterprise audit export: `meta/audit-export-policy.yaml`
- dedicated deployment profile: `meta/dedicated-deployment-profile.yaml`
- enterprise control matrix: `meta/enterprise-control-matrix.yaml`
- retention and SLO policy: `meta/retention-slo-policy.yaml`

## Security model summary

### Human auth
- OIDC or SAML for human operators
- short-lived session tokens for UI sockets
- operator identity must flow into timeline events and audit

### Machine auth
- mTLS or workload identity between internal services
- scoped credentials for workers
- capability tokens for effectful tool and browser execution

### Authorization
Use **RBAC + ABAC**:
- RBAC for coarse role membership
- ABAC for runtime context such as tenant, workspace, tool risk, environment, data sensitivity, and control mode

### Secret handling
- secrets come from external secret manager / KMS path
- workers receive narrow credentials or capability tokens, not broad tenant secrets
- session timelines must not store raw secrets
- artifacts containing sensitive payloads must support redaction and retention rules

### Enterprise deployment hardening
- Tier C dedicated deployment uses a dedicated control plane, dedicated worker pools, and dedicated object store
- key isolation flows through a dedicated KMS namespace and per-tenant wrapping keys
- database, object-store, and key region pins form the data residency hook set
- audit export bundles remain tenant/workspace scoped and use signed-url rehydration for artifact evidence

## Dangerous action boundaries

Treat these as dangerous by default:
- browser mutations
- destructive actions
- financial actions
- outbound communication
- PII export
- privilege changes
- bulk operations

These classes are listed in `meta/dangerous-action-classes.yaml` and should usually require explicit approval or stronger policy checks.

## Audit model

Audit comes from the session timeline plus supporting operational logs.
Must be attributable:
- operator actions
- approval decisions
- policy results
- dangerous-action dispatches
- redactions
- lease loss and adoption
- session quarantine

See `docs/design-docs/security-governance.md` and `docs/threat-models/`.
