# Overload response

This runbook anchors PHASE-16 overload handling.

## Trigger

Use this when queue depth, projector lag, artifact-index lag, or cohort-query latency
crosses a modeled threshold in `meta/load-shed-policies.yaml`.

## Steps

1. Confirm which overload policy fired and whether it is at soft or hard pressure.
2. Verify protected classes still include operator control, recovery, and approved
   effectful work.
3. Confirm the delayed or rejected shed classes match the policy rather than operator
   intuition.
4. Record the triggering metric, threshold, and affected pool or cohort.
5. If the pressure is tenant-specific, hand off to the hot-tenant isolation runbook.

## Never do this

- drop operator-critical traffic without a policy change
- use "temporary" ad hoc queue filters as a hidden override
- preserve convenience traffic at the expense of recovery
