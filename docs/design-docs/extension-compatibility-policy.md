# Extension compatibility policy

This document defines the bounded compatibility promises for third-party extensions in PHASE-10.

## Goal

Let extensions evolve without turning compatibility into guesswork or allowing adapters to smuggle in uncontrolled runtime assumptions.

## Version axes

Every third-party extension must declare compatibility across four axes:

- manifest version
- `runtime_contract_version`
- `extension_api_version`
- compatibility ranges for Aegis runtime release, extension API, and tool-registry version

The machine-readable policy lives in `meta/extension-compatibility-policy.yaml`.

## Required rules

- runtime-release compatibility must declare explicit `min` and `max`
- extension-API compatibility must declare explicit `min` and `max`
- tool-registry compatibility must declare explicit `min` and `max`
- open-ended ranges are forbidden
- lifecycle hooks must remain explicit
- capability boundaries must remain explicit
- sample extension-pack evidence is required for review
- review rubric coverage is required for review
- MCP adapters remain external-only boundaries

## Current supported baseline

- current Aegis runtime release: `0.10.0`
- supported runtime contract versions: `v1`
- current extension API version: `v1alpha1`
- current tool-registry version: `v1`

## Deprecation posture

- breaking extension-API changes require at least 90 days notice
- only one parallel extension-API version is supported at this phase
- sample fixtures must be refreshed when compatibility semantics change

## Review consequence

An extension is not review-ready unless its manifest, compatibility ranges, sample pack, and review rubric all agree with the machine-readable policy.
