# Projection model

This document defines the stable operator-facing projection contracts.

## Rule

Operator surfaces must read from stable projections, not hidden SessionKernel internals.

## Canonical projection

The canonical operator-facing view is:
- `schema/proto/aegis/runtime/v1/operator.proto`
- `schema/jsonschema/operator-session-view.schema.json`

Fields that must always be present before operator-console work begins:
- tenant/workspace/session identity
- owner node
- lease epoch
- phase / control mode / health
- wait reason
- last committed seq_no
- latest checkpoint id
- deadlines
- pending approvals
- in-flight actions
- recent artifacts
- fenced/degraded state
- latest recovery reason

## Projection sources

- session lifecycle fields from the checkpoint + event tail
- in-flight action ledger from authoritative session state
- approvals from approval ledger / checkpoint
- artifact metadata from artifact table, never raw object bytes

## Anti-patterns

- building the console directly from raw event payloads
- keeping approval state only in the browser UI
- hiding lease or recovery state from operators
