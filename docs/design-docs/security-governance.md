# Security and governance model

This document defines the implementation-level trust model for Aegis.

## Machine-readable sources

- roles: `meta/rbac-roles.yaml`
- attributes: `meta/abac-attributes.yaml`
- dangerous action classes: `meta/dangerous-action-classes.yaml`
- failure/runbook mapping: `meta/failure-runbooks.yaml`
- capability-token claims: `schema/jsonschema/capability-token-claims.schema.json`
- approval request shape: `schema/jsonschema/approval-request.schema.json`
- artifact evidence shape: `schema/jsonschema/artifact-metadata.schema.json`

## Control surfaces

- operator and API reads are gated by RBAC and ABAC catalogs before tenant-scoped data leaves the control plane
- effectful actions are classified by dangerous-action class, evaluated by policy, and escalated through approvals when required
- capability tokens bind approved effectful work to tenant, workspace, session, action, worker kind, scope, and expiry
- quota and admission control are part of correctness for live sessions, concurrent browser contexts, and concurrent effectful actions
- worker routing is tier-aware through durable `isolation_tier`, `worker_pool_id`, and `dispatch_route_key` fields
- artifacts remain evidence objects with retention and redaction state, not opaque debug leftovers

## Current implementation rules

- capability tokens are required for effectful actions
- dangerous browser writes default to `allow_with_constraints`, `require_approval`, or `deny` based on the machine-readable dangerous-action class
- tenant and workspace identity must be carried across canonical tables, checkpoints, outbox rows, execution metadata, and operator-facing payloads
- RBAC/ABAC checks govern session fleet, session detail, replay, approvals, and audit-export surfaces with tenant/workspace scoping
- live-session admission is enforced before a session host starts, while browser-context and effectful-action admission are enforced before execution-bridge dispatch
- Tier B and Tier C dispatches use tenant-scoped route keys while worker registrations advertise `worker_pool_id` and `isolation_tier`
- worker payloads are least-privilege and may not contain broad tenant secrets
- audit and redaction evidence must remain traceable through runtime events, approval records, capability-token references, and artifact metadata

## Audit and evidence path

- `action.requested`, `approval.requested`, `approval.granted`, `approval.denied`, `action.dispatched`, and worker terminal events preserve the dangerous-action and approval trail
- replay and operator detail views expose policy decisions, pending approvals, routed isolation metadata, and artifact references from the timeline
- artifact metadata carries `retention_class`, `redaction_state`, sensitivity, tenant/workspace linkage, and storage location for later audit export
- failure classes map to concrete operator surfaces and runbooks through `meta/failure-runbooks.yaml`
