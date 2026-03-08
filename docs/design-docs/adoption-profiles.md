# Adoption profiles

This document defines the PHASE-19 adoption-profile surface for serious Aegis adopters.

## Goal

Make first-adopter readiness explicit enough that onboarding does not depend on hidden repo lore.

## Why profiles exist

Not every adopter starts from the same operating context.
A shared-cloud evaluation team and a regulated enterprise rollout both need Aegis,
but they do not need the same deployment track, drill cadence, or evidence prerequisites.

The machine-readable source is `meta/adoption-profiles.yaml`.

## Profile fields

Each profile binds:

- adopter class
- reference deployment track
- golden-path starter kit
- required evidence bundles
- required operator exercises
- onboarding runbook

That keeps adoption tied to already implemented runtime proof rather than generic setup prose.

## Boundaries

Adoption profiles do not create a second product model.
They package already implemented guarantees into bounded readiness paths.
They must not weaken:

- single-owner semantics
- replay and checkpoint discipline
- policy and approval boundaries
- sandbox and governance rules for extensions
