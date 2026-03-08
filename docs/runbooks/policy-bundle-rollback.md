# Policy bundle rollback

Use this runbook when an ecosystem policy bundle must be reverted.

## Preconditions

- the affected bundle id is known
- the affected extension kinds and tenant tiers are known
- the rollback keeps extensions inside the bounded sandbox surface

## Rollback steps

1. identify the prior approved policy bundle definition
2. confirm the rollback keeps dual-control obligations intact
3. confirm rollback runbook and explanation fields remain present
4. regenerate policy-bundle and ecosystem evidence reports
5. revoke or pause public compatibility publication if the rollback changes certified posture

## What must not happen

- no direct extension enablement outside the policy bundle
- no bypass of sandbox-profile assignments
- no public compatibility publication without regenerated evidence
