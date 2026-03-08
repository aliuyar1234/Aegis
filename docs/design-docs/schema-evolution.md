# Schema Evolution

## Purpose

PHASE-15 introduces explicit upcaster manifests for historical event and checkpoint
versions.
The goal is to make replay compatibility visible and reviewable.

## Canonical machine-readable artifact

- `meta/upcaster-manifests.yaml`

## Design rules

- historical payloads are not assumed to be magically readable forever
- version transitions are explicit and typed
- unsupported historical versions fail with an incompatibility boundary instead of
  being silently coerced

## Non-goals

- destructive rewriting of all historical events by default
- hidden migrations embedded only in application code
