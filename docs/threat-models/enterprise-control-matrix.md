# Enterprise control matrix

This document supports PHASE-13.

Phase 09 provides the implementation-grade trust boundary that PHASE-13 later hardens into enterprise packaging and deployment controls.

## Current control map

| Control area | Current implementation path | Evidence sources |
|---|---|---|
| Identity and scoped authz | OIDC-ready actor context feeds RBAC/ABAC checks on operator and API surfaces. | `meta/rbac-roles.yaml`, `meta/abac-attributes.yaml`, `apps/aegis_policy/lib/aegis/policy/authorizer.ex` |
| Tenant and workspace scoping | Canonical tables, checkpoints, outbox rows, dispatch metadata, and operator payloads carry tenant/workspace scope. | `docs/design-docs/storage-model.md`, `apps/aegis_events/lib/aegis/events/store.ex`, `apps/aegis_gateway/lib/aegis/gateway/operator_console.ex` |
| Quota and admission control | Live sessions, concurrent browser contexts, and concurrent effectful actions are admitted before runtime start or dispatch. | `docs/design-docs/multitenancy.md`, `apps/aegis_runtime/lib/aegis/runtime/admission_control.ex`, `apps/aegis_execution_bridge/lib/aegis/execution_bridge/admission_control.ex` |
| Tiered isolation routing | Isolation tiers drive routed dispatch subjects, worker-pool affinity, and replay-visible routing metadata. | `docs/design-docs/transport-topology.md`, `apps/aegis_policy/lib/aegis/policy/evaluator.ex`, `apps/aegis_execution_bridge/lib/aegis/execution_bridge/transport_topology.ex` |
| Dangerous-action governance | Tool descriptors classify dangerous actions; policy, approvals, and capability tokens constrain writes. | `schema/tool-registry.yaml`, `meta/dangerous-action-classes.yaml`, `schema/jsonschema/capability-token-claims.schema.json` |
| Audit, evidence, and replay | Runtime events and artifacts preserve approvals, policy decisions, routing metadata, and operator interventions for replay. | `docs/design-docs/security-governance.md`, `schema/jsonschema/artifact-metadata.schema.json`, `apps/aegis_projection/lib/aegis/projection/session_replay.ex` |
| Redaction and retention | Artifact metadata and replay surfaces preserve redaction state and retention class without rewriting history. | `docs/design-docs/storage-model.md`, `schema/jsonschema/artifact-metadata.schema.json`, `docs/threat-models/runtime-threat-model.md` |
| Runbooks and operator recovery | Failure classes map to explicit runbooks and operator surfaces for escalation and recovery. | `meta/failure-runbooks.yaml`, `docs/runbooks/`, `docs/product-specs/operator-console.md` |

## Enterprise follow-on

- identity federation still needs full enterprise deployment integration in PHASE-13
- Tier C dedicated deployment, key isolation, and packaging remain later-phase hardening
- audit export pipelines and retention automation remain bounded by the future enterprise pass
