# Runtime threat model

## Assets to protect

- session timelines
- approvals and policy decisions
- tenant isolation
- capability tokens
- artifact metadata and contents
- operator identity and actions
- lease ownership state

## Trust boundaries

- human operators ↔ control plane
- control plane ↔ execution plane
- execution plane ↔ external tools/browsers
- control plane ↔ object storage
- tenant ↔ tenant

## Primary threats

- stale or forged ownership acting after lease loss
- worker using credentials outside approved action scope
- cross-tenant data leakage through artifacts or logs
- hidden dangerous actions not entering the timeline
- replay corruption or event tampering
- redaction bypass through raw artifact access
- operator overreach beyond role and workspace

## Required controls

- lease epochs and fencing
- capability tokens with narrow scope and expiry
- universal tenant/workspace scoping
- quota and admission control for live sessions and effectful execution
- durable `isolation_tier`, `worker_pool_id`, and routed dispatch metadata for higher-isolation tenants
- event integrity checks
- audit trail for operator and approval actions
- signed URL controls for artifacts
- artifact retention and redaction metadata preserved alongside timeline evidence
- RBAC/ABAC enforcement on console and API surfaces
