# OSS / managed release policy

This document defines the release, upgrade, and compatibility rules for the PHASE-12 split.

## Goal

Keep OSS core and managed offerings on one architecture line while making contract, migration, and operator-documentation obligations explicit.

## Canonical policy artifact

The machine-readable policy lives in `meta/split-release-policy.yaml`.

The per-flavor release manifest lives in `meta/split-release-manifest.yaml`.

## Contract policy

- runtime contract changes require an explicit version bump
- OSS and managed offerings follow the same runtime contract line
- JSON Schema changes require fixture refresh
- managed-only schema forks are forbidden
- managed add-ons cannot bypass the extension compatibility policy

## Migration policy

Every flavor must declare:

- upgrade strategy
- migration owner
- required documentation references

OSS local remains self-managed.
Shared cloud and isolated execution add provider-managed rollout duties.
Dedicated deployment adds change-window and preflight obligations.

## Operator-facing documentation obligations

Split-surface compatibility policy must cover contracts, migrations, and operator-facing documentation obligations.

That means:

- operator console docs must be updated when managed surfaces change what operators can see or do
- new managed-only failure modes must add runbook references
- every flavor needs explicit release notes and upgrade guidance
- the OSS/managed phase gate must be refreshed when the split boundary changes

## Guardrails

- OSS manifests must not reference managed-only surfaces
- managed catalogs must reference the OSS capability they build on
- packaging and release matrices must cover every locked flavor

The split is allowed to change packaging and operations.
It is not allowed to create a hidden managed runtime fork.
