# GA transition review

Use this runbook when deciding whether Aegis can move from bounded rollout to a
GA-style customer posture.

## Inputs

- `meta/ga-transition-gate-manifest.yaml`
- the current phase-22, phase-23, phase-24, and phase-25 evidence bundles
- rollout, production-readiness, service-scale, and scorecard docs

## Workflow

1. verify the required inputs, evidence refs, runbooks, and Make targets still exist
2. confirm the rollout and production-isolation surfaces are still current
3. confirm service-scale support and rollout scorecards still pass review
4. produce the GA transition report before making an expansion decision

## Exit condition

GA transition is ready only when rollout-program readiness, production-isolation
readiness, service-scale readiness, and rollout scorecards pass together.
