# PHASE-21 - Fresh-clone onboarding and official evaluation deployment

**Status:** completed

## Phase goal

Turn the first-clone and first-deployment experience into an explicit, reproducible,
repo-native path instead of a collection of implied commands and local lore.

## Why this phase exists

PHASE-20 closed the internal maturity arc, but a strong internal runtime is not
the same thing as software a new engineer or evaluator can install and reason
about without help. Before broader customer-facing work, the repo needs an official
onboarding path and an official evaluation deployment path.

## Scope

- canonical first-clone read order and entrypoint alignment
- official first-run commands for local evaluation
- cross-platform bootstrap, init, and smoke scripts for the supported evaluation path
- a machine-checkable evaluation deployment profile tied to the committed local stack
- operator-facing docs for first evaluation and deployment boundaries

## Non-goals

- production Kubernetes packaging
- managed-cloud rollout automation
- pilot-customer support policy
- release-candidate signoff bundles
- commercial packaging or pricing

## Prerequisites

PHASE-20

## Deliverables

- fresh-clone onboarding contract with canonical docs and first-run commands
- official evaluation deployment guide
- official evaluation Make targets layered over the local compose stack
- cross-platform bootstrap/init/smoke scripts
- machine-checkable evaluation deployment profile and report

## Detailed tasks

- `P21-T01` - Fix canonical entrypoints and formalize fresh-clone onboarding
- `P21-T02` - Promote the local compose stack to the official evaluation deployment path

## Dependencies

- prerequisites: PHASE-20
- unlocks after exit: none yet

## Risks

- documenting an onboarding story that still depends on hidden platform assumptions
- calling the local stack "official" without pinning services, ports, init steps, and smoke checks
- leaving the repo entrypoint surfaces misaligned even after adding more docs

## Test plan

- `TS-057` - Fresh-clone onboarding validation (`pytest tests/launch_readiness/test_phase21_onboarding_assets.py -q`)
- `TS-058` - Evaluation deployment validation (`pytest tests/launch_readiness/test_phase21_evaluation_deployment_assets.py -q`)

## Acceptance criteria

- `AC-097` - Fresh-clone onboarding is modeled as a machine-checkable repo surface with aligned read order, first-run commands, and canonical entrypoint documents instead of relying on tribal setup knowledge.
- `AC-098` - The local compose stack is promoted to an official evaluation deployment path with explicit services, ports, init flow, smoke flow, and operator-facing documentation.

## Exit criteria

- the onboarding manifest, evaluation deployment profile, docs, and runner scripts exist and validate;
- `make bootstrap`, `make eval-up`, `make eval-init`, `make eval-check`, and `make smoke` form the canonical first-run path;
- the repo and README point newcomers at actual existing docs instead of stale or implicit setup paths;
- the phase registry, task graph, acceptance criteria, and suite registry stay synchronized.

## What becomes unlocked after this phase

none yet
