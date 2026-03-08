# PHASE-25 - GA transition, repeatable customer rollout, and service-scale readiness

**Status:** completed

## Phase goal

Turn the bounded PHASE-24 pilot posture into an explicit SSOT program for repeatable
customer rollout, GA governance, tenant-isolated production readiness, and scaled
service operations.

## Why this phase exists

PHASE-24 made the first pilot wave, control-room motion, feedback loop, exception
handling, and exit review explicit. The next gap is the transition from "one bounded
design-partner wave" to "repeatable customer launch motion" without falling back to
founder judgment, bespoke operations, or unclear production-isolation boundaries.

## Scope

- repeatable customer rollout program after the bounded pilot
- GA-governance and launch-decision surfaces
- tenant-isolated production readiness and migration boundaries
- service-scale support and operations cadence
- rollout scorecards and reference-customer evidence surfaces

## Non-goals

- mass-market self-serve onboarding
- pricing, billing, or commercial packaging
- unbounded product expansion unrelated to rollout repeatability
- managed-cloud automation beyond committed rollout governance
- replacing launch evidence with anecdotal pilot narratives

## Prerequisites

PHASE-22, PHASE-23, and PHASE-24

## Deliverables

- repeatable customer rollout program definition
- GA decision and expansion governance surfaces
- tenant-isolated production-readiness and migration boundaries
- service-scale support and operations readiness surfaces
- rollout scorecard and reference-customer evidence bundle plan

## Detailed tasks

- `P25-T01` - Define the repeatable customer rollout program for post-pilot cohorts
- `P25-T02` - Define tenant-isolated production readiness and migration boundaries
- `P25-T03` - Define service-scale support and operating cadence for multi-customer launch
- `P25-T04` - Define rollout scorecards and reference-customer evidence surfaces
- `P25-T05` - Gate GA transition on rollout program, production isolation, service-scale readiness, and scorecard evidence

## Dependencies

- prerequisites: PHASE-22, PHASE-23, PHASE-24
- unlocks after exit: none yet

## Risks

- stretching a bounded pilot operating model into GA without repeatable rollout rules
- treating tenant-isolated production readiness as implied by pilot success
- scaling support obligations before explicit service ownership and scorecards exist

## Test plan

- `TS-074` - Repeatable rollout program validation
- `TS-075` - Tenant-isolated production readiness validation
- `TS-076` - Service-scale operations readiness validation
- `TS-077` - Rollout scorecard validation
- `TS-078` - GA transition gate and evidence validation

## Acceptance criteria

- `AC-114` - PHASE-25 defines an explicit repeatable customer rollout program that turns PHASE-24 pilot execution into bounded post-pilot cohort rules, launch handoffs, and rollout decision classes.
- `AC-115` - PHASE-25 defines tenant-isolated production readiness and migration boundaries so that post-pilot customer launches are not treated as pilot-shaped exceptions.
- `AC-116` - PHASE-25 defines service-scale support and operating cadence for multi-customer launch instead of extending founder-led pilot support indefinitely.
- `AC-117` - PHASE-25 defines rollout scorecards and reference-customer evidence surfaces so launch expansion is grounded in reproducible proof instead of anecdotal success claims.
- `AC-118` - PHASE-25 defines a GA transition gate that binds rollout-program readiness, production-isolation readiness, service-scale support, and rollout scorecards into an explicit launch-decision surface.

## Exit criteria

- the phase-25 manifests, docs, runner scripts, gates, and evidence bundle exist and validate
- `make ga-check` produces passing rollout, isolation, service-scale, scorecard, and GA-transition results
- rollout expansion, production-isolation boundaries, and GA governance are reviewable from committed repo evidence alone

## What becomes unlocked after this phase

PHASE-26 - Live customer operations, release automation, and field evidence governance
