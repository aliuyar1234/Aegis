# Extension Sunset

Use this runbook when applying a PHASE-20 deprecation or sunset policy.

## Inputs

- the relevant policy in `meta/deprecation-governance.yaml`
- the affected certified pack, starter kit, or rollout track
- the listed successor references and freeze actions

## Steps

1. Confirm the affected asset identifiers match the current certified or rollout surface.
2. Verify the notice window and successor references.
3. Apply the listed freeze actions for the affected surface.
4. Keep rollback or suspension instructions available while the sunset is active.
5. Do not remove evidence references until the migration or successor path is explicit.

## Exit condition

A sunset is considered controlled only when notice, successor, freeze, and rollback
surfaces are all committed and reviewable.
