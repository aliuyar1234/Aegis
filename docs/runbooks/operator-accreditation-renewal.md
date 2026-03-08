# Operator Accreditation Renewal

Use this runbook when renewing a PHASE-20 operator accreditation track.

## Inputs

- the accreditation track in `meta/operator-accreditation.yaml`
- the required evidence bundles referenced by that track
- the linked operator exercises from `meta/operator-exercise-manifest.yaml`

## Steps

1. Confirm the operator is renewing the correct accreditation track for the target deployment track.
2. Verify that every referenced evidence bundle still exists and is current in the repo.
3. Re-run the linked operator exercises or confirm their latest bounded evidence.
4. Confirm that the renewal window has not expired without review.
5. Record any restricted or elevated actions that remain in scope for the track.

## Exit condition

Renewal is complete only when the accreditation track still lines up with committed
exercises, evidence, and deployment surfaces.
