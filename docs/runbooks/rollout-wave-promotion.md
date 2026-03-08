# Rollout-Wave Promotion

Use this runbook when promoting a PHASE-20 rollout wave.

## Inputs

- the target rollout wave in `meta/rollout-wave-manifest.yaml`
- the referenced deployment track from `meta/reference-deployment-tracks.yaml`
- current evidence bundles listed in the wave

## Steps

1. Verify the rollout wave still points to the intended deployment track and flavor.
2. Confirm the required accreditation track is current.
3. Review the listed evidence bundles and promotion criteria.
4. Validate the applicable change window before promotion.
5. Keep rollback and customer-notice references ready before moving the wave forward.

## Exit condition

A wave is promotable only when evidence, accreditation, and rollback surfaces are
all present and coherent.
