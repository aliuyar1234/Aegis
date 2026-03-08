# Tenant production cutover

Use this runbook when moving a customer from bounded pilot operations into a tenant-isolated
production posture.

## Workflow

1. open `meta/tenant-isolated-production-readiness.yaml`
2. verify the required evidence, migration boundaries, and rollback runbooks are current
3. confirm the dedicated-tenant and environment-readiness inputs are still valid
4. fail the cutover if any production-isolation boundary is undocumented

## Do not do this

- do not treat production cutover as a pilot-shaped exception
- do not cut over without explicit rollback boundaries
