# Policy bundles

This document defines the PHASE-18 delegated-governance bundle surface for extensions.

## Goal

Treat extension governance as an explicit policy bundle with rollback discipline, not as a bag of reviewer notes.

## Bundle inputs

Each policy bundle binds extension admission to canonical repo sources:

- tool registry
- dangerous-action catalog
- RBAC catalog
- ABAC attribute catalog
- extension compatibility policy

The machine-readable source is `meta/policy-bundle-profiles.yaml`.

## Why bundles exist

By PHASE-18, extension review needs to answer more than "does this schema validate?"
It must also answer:

- which tenant tiers can use the extension?
- which extension kinds are governed by the bundle?
- who must approve policy changes?
- how do operators roll back a bundle safely?
- which fields must be explainable during review?

Policy bundles keep those answers reproducible.

## Dual control

Third-party ecosystem bundles require explicit approval roles and a rollback runbook.
That keeps governance bounded even when the extension pack itself is technically valid.

## Explanation fields

Every bundle declares the fields reviewers and operators must be able to explain.
The explanation list exists so that later tooling cannot hide important risk dimensions behind a green checkmark.
