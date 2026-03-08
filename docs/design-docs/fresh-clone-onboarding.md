# Fresh-clone onboarding

This document defines the first-clone onboarding contract for Aegis.

## Why this exists

The repo already has strong architecture, validation, and phase discipline. That
does not automatically give a new engineer a reliable first-run path. The first-clone
surface must be explicit because onboarding drift is one of the fastest ways to
turn a strong runtime repo back into founder-only infrastructure.

## Canonical entrypoints

The onboarding path starts from:

- `README.md`
- `AGENTS.md`
- `docs/operations/evaluation-deployment.md`
- `docs/runbooks/fresh-clone-first-run.md`

The read order and first-run commands in those surfaces must stay aligned.

## Canonical first-run path

The official first-run command sequence is:

1. `make bootstrap`
2. `make eval-up`
3. `make eval-init`
4. `make eval-check`
5. `make smoke`

This sequence is intentionally repo-native and must not depend on undocumented local shell aliases.

## Constraints

- onboarding docs must point only at files that exist
- bootstrap, init, and smoke steps must be invokable through committed scripts
- the evaluation path must use the committed local stack and not a hidden ad hoc environment
- first-clone onboarding is docs-first, but the critical parts are machine-checkable through manifests and tests

## Non-goals

- replacing the architecture docs
- production deployment guidance
- customer pilot runbooks
- generic developer portal work
