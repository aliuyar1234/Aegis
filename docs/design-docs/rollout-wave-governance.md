# Rollout-Wave Governance

This document defines the PHASE-20 rollout-wave surface for Aegis.

## Why rollout waves exist

PHASE-19 made reference deployment tracks explicit.
PHASE-20 makes their promotion path explicit too: which change window applies, what
evidence must be current, what accreditation track is required to run the wave, and
what rollback surface exists if the promotion must stop.

## Core rules

- A rollout wave must reference a committed deployment track.
- The referenced deployment flavor must stay consistent with that track.
- Promotion criteria must point at committed evidence, not verbal sign-off.
- Rollback and customer-notice surfaces must exist before the wave is considered valid.

## Non-goals

- no hidden release-train state machine
- no implied runtime-mode change outside the committed deployment tracks
- no broad SaaS rollout tooling outside the repo SSOT
