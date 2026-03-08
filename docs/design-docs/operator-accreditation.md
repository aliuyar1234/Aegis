# Operator Accreditation

This document defines the PHASE-20 operator accreditation surface for Aegis.

## Why accreditation exists

PHASE-06 through PHASE-19 proved that operators can inspect sessions, intervene,
run drills, and guide first adopters.
PHASE-20 turns that from "operators should know this" into an explicit contract:
which exercises must be completed, what evidence must be current, what deployment
tracks the operator is accredited for, and how renewal happens.

## Boundaries

- Accreditation does not bypass policy, approvals, or capability-token checks.
- Accreditation does not grant hidden runtime authority beyond already modeled operator actions.
- Accreditation is deployment-track-specific so shared and dedicated operations do
  not collapse into one generic role.

## Required links

Accreditation tracks must bind:

- committed operator exercises from PHASE-19
- current evidence bundles from PHASE-15 onward
- explicit deployment tracks
- bounded allowed actions
- renewal cadence and renewal runbook

## Failure mode to avoid

Do not treat operator seniority or org-chart position as the source of truth.
The repo must stay able to prove why an operator track is considered current and
what runtime surfaces it covers.
