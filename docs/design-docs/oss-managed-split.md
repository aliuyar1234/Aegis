# OSS / managed split

This document defines the PHASE-12 boundary between OSS core and managed-only value.

## Goal

Make the split explicit enough that packaging, release, and extension expectations stop being implied knowledge.

## Boundary principles

- OSS core remains the canonical runtime line
- managed offerings add operational services, packaging, and isolation layers
- managed surfaces must build on the same control-plane contracts rather than a hidden runtime fork
- dedicated deployment is a packaging and isolation flavor, not a second event model

## OSS core

The machine-readable OSS manifest lives in `meta/oss-core-manifest.yaml`.

OSS core includes:

- session kernel and authoritative runtime ownership
- event log, checkpoints, replay, and leases
- transport contracts and execution bridge
- local operator console baseline
- browser wedge reference implementation harness
- schemas, fixtures, and validation surfaces needed to self-host the runtime

OSS core explicitly excludes managed-only control-plane services, packages, and operational features.

## Managed-only surfaces

The machine-readable managed catalog lives in `meta/managed-surface-catalog.yaml`.

Managed-only surfaces include:

- hosted multitenancy control plane services
- shared-cloud and isolated-execution routing operations
- hosted observability, incident response, and coordinated upgrade operations
- managed audit export and enterprise integration packaging
- dedicated deployment management and change-window coordination

## Guardrails

- managed services may not become hidden prerequisites for replay, policy, or operator truth
- OSS releases must remain self-managed with Postgres, JetStream, and object storage
- managed packages may add automation, tenancy operations, and support boundaries
- managed packages may not add alternate canonical state paths

## Related artifacts

- `meta/deployment-flavors.yaml`
- `meta/split-release-policy.yaml`
- `meta/split-release-manifest.yaml`
- `docs/references/packaging-matrix.md`
- `docs/references/release-upgrade-matrix.md`
