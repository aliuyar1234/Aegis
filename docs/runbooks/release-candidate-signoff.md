# Release candidate signoff

Use this runbook when confirming that an Aegis release candidate is ready for customer-facing evaluation or rollout.

## Inputs

- the launch signoff manifest in `meta/release-signoff-manifest.yaml`
- current release evidence bundle
- restore drill references
- rollback runbooks
- support and evaluation docs

## Workflow

1. verify the required evidence references are present
2. confirm the restore drill identifiers and rollback runbooks are still current
3. confirm the evaluation workflow targets are still available in `Makefile`
4. produce the signoff report before moving to launch-readiness evidence

## Exit condition

Signoff is ready only when release evidence, restore proof, rollback surfaces, and evaluation targets all pass together.
