# Hot-tenant isolation

This runbook anchors PHASE-16 noisy-neighbor response.

## Trigger

Use this when a tenant or workflow class is identified as the cause of repeated queue
pressure, browser-context exhaustion, projector lag, or artifact-index lag.

## Steps

1. Identify the matching isolation profile in `meta/isolation-profiles.yaml`.
2. Confirm the tenant tier and workflow class match the profile scope.
3. Apply only the mitigation actions listed in the profile.
4. Verify preserved classes remain available for unaffected tenants and for operator
   or recovery work.
5. Record the applied isolation action, the causing workload, and any linked runbooks.

## Never do this

- hard-code a bespoke tenant bypass into runtime code
- widen isolation beyond the declared profile without recording the reason
- treat isolation as a replacement for bounded capacity planning
