# PHASE-24 - Design-partner pilot execution, operating cadence, and exit review

**Status:** completed

## Phase goal

Turn the PHASE-23 launch-governed pilot posture into explicit machine-checkable
surfaces for executing the first bounded design-partner wave, operating it, triaging
feedback and exceptions, and deciding whether to expand, hold, or stop.

## Why this phase exists

PHASE-23 defined the launch-governance and pre-customer proof needed before a pilot
could responsibly begin, but it still left the pilot itself as an implied operating
motion. Aegis now needs explicit repo-native surfaces for launch-wave composition,
launch-day control-room operations, feedback and issue triage, exception handling,
and pilot exit review.

## Scope

- bounded design-partner pilot launch waves
- launch-day and steady-state pilot control-room operations
- customer feedback and issue triage loop
- launch exception governance and containment paths
- pilot exit review and rollout recommendation evidence

## Non-goals

- broad customer GA rollout
- managed-cloud automation beyond bounded pilot operations
- unbounded product customization during the pilot
- pricing, billing, or commercial packaging
- replacing runtime evidence with narrative-only pilot notes

## Prerequisites

PHASE-20, PHASE-22, and PHASE-23

## Deliverables

- pilot launch-wave manifest for the first bounded cohort
- pilot control-room manifest for launch-day and steady-state operations
- customer feedback and issue triage manifest
- launch exception governance manifest
- pilot exit review manifest and pilot operations evidence bundle

## Detailed tasks

- `P24-T01` - Define bounded pilot launch waves for the first design-partner cohort
- `P24-T02` - Define launch-day and steady-state pilot control-room operations
- `P24-T03` - Define the pilot customer feedback and issue triage loop
- `P24-T04` - Define launch exception governance for bounded pilot operations
- `P24-T05` - Gate pilot execution on exit review and a reproducible pilot operations evidence bundle

## Dependencies

- prerequisites: PHASE-20, PHASE-22, PHASE-23
- unlocks after exit: none yet

## Risks

- letting pilot execution drift into informal founder-led coordination
- losing clear boundaries between launch exceptions, support escalations, and rollback conditions
- collecting pilot feedback without an explicit evidence and decision loop

## Test plan

- `TS-069` - Pilot launch-wave validation
- `TS-070` - Pilot control-room validation
- `TS-071` - Customer feedback loop validation
- `TS-072` - Launch exception governance validation
- `TS-073` - Pilot exit review and evidence-bundle validation

## Acceptance criteria

- `AC-109` - PHASE-24 defines explicit design-partner launch waves that bind pilot cohorts to committed deployment tracks, golden paths, and the PHASE-23 go/no-go evidence bundle.
- `AC-110` - PHASE-24 defines launch-day and steady-state pilot control-room operations with explicit roles, handoffs, observability surfaces, and escalation runbooks.
- `AC-111` - PHASE-24 defines a customer feedback and issue triage loop that binds pilot learnings to evidence, ownership, and decision classes instead of ad hoc founder memory.
- `AC-112` - PHASE-24 defines launch exception governance with explicit trigger classes, containment paths, approvals, and rollback boundaries for bounded pilot operations.
- `AC-113` - PHASE-24 captures pilot execution status, launch exceptions, customer feedback, and rollout recommendation in a reproducible pilot operations evidence bundle and exit review surface.

## Exit criteria

- the phase-24 manifests, docs, runner scripts, gates, and evidence bundle exist and validate
- `make pilot-check` produces passing launch-wave, control-room, feedback, exception, and exit-review results
- the first bounded pilot operating motion is explicit enough to review from committed repo evidence alone

## What becomes unlocked after this phase

PHASE-25 - GA transition, repeatable customer rollout, and service-scale readiness
