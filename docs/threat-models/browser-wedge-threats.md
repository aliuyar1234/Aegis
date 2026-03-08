# Browser wedge threats

## Wedge-specific risks

- accidental browser writes without approval
- browser context leakage between tenants
- untrusted page content influencing prompt or action assembly
- screenshots or DOM snapshots containing restricted data
- operator takeover bypassing policy boundaries
- uncertain writes after browser worker crash
- credential leakage into browser automation logs

## Controls

- browser writes default to higher-risk classes and pass through policy, approval, and capability-token checks before dispatch
- browser contexts are tenant-scoped and not reused across tenants
- browser-context and mutating-action dispatches are subject to tenant/workspace quota admission before work leaves the control plane
- Tier B and Tier C dispatches use routed subjects with durable `worker_pool_id`, `dispatch_route_key`, and `isolation_tier` metadata for replay and audit
- raw artifacts carry sensitivity, `retention_class`, and `redaction_state` metadata
- before/after screenshots, DOM snapshots, traces, and uncertainty markers form the evidence set for effectful writes
- operator takeover is a mode change in the timeline and still passes through RBAC/ABAC authorization on control surfaces
- capability tokens scope allowed action and arguments
- uncertain side effects escalate to human review and runbook-driven recovery
- worker logs must avoid raw secrets and use redaction hooks
