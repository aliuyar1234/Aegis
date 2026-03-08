# Dedicated key isolation

## When to use

Use this runbook when a Tier C dedicated deployment shows KMS namespace drift, secret-manager access degradation, or residency/key-pin mismatch.

## Signals

- dedicated key rotation misses its change window
- KMS namespace or wrapping-key lookup fails
- database, object store, and key region pins diverge
- break-glass access is required for tenant key recovery

## Immediate checks

- confirm the tenant is operating in the dedicated deployment profile
- confirm KMS namespace, wrapping-key reference, and object-store region pin
- confirm the secret manager still issues scoped credentials only
- confirm cross-region failover was not activated without operator approval

## Containment

- stop non-essential rotation or export operations until key lineage is clear
- preserve current encryption metadata and recent artifact references as evidence
- keep the tenant in bounded degraded mode rather than silently widening key access

## Recovery

- restore the dedicated KMS namespace or wrapping-key mapping
- complete rotation only inside the approved change window
- rerun the dedicated-tenant evidence preflight
- document the recovery in the enterprise acceptance trail
