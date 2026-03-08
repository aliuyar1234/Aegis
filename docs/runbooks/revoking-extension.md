# Revoking an extension

Use this runbook when a certified or publicly listed extension pack must be revoked.

## Trigger conditions

- compatibility drift beyond the supported range
- sandbox-profile mismatch
- policy-bundle rollback
- missing recertification evidence
- operator evidence that the extension no longer meets the certified surface

## Response

1. identify the affected pack and its certification report
2. identify the governing policy bundle and sandbox profiles
3. remove the public track or mark it non-publishable
4. revoke the certification level in the machine-readable certification surface
5. regenerate the ecosystem evidence bundle

## Evidence to preserve

- certification candidate id
- sandbox profile assignments
- governing policy bundle id
- public track id if one exists
- regenerated ecosystem evidence bundle
