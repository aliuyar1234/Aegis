# Schema and contract versioning

## Runtime contracts

- Protobuf follows additive-first evolution.
- Breaking runtime changes require new message fields or new versioned messages plus a migration plan.
- `buf.yaml` and `buf.gen.yaml` are the canonical generation configs.

## Events

- Every event type has `version` in `schema/event-catalog/events.yaml`.
- Payload schemas live in `schema/event-payloads/` and must be versioned explicitly if changed incompatibly.

## Checkpoints

- Checkpoints are versioned independently from events.
- The current canonical checkpoint schema is `schema/checkpoints/session-checkpoint-v1.schema.json`.

## Tool I/O and operator views

- Tool descriptors and related payloads use JSON Schema.
- Capability-token claims, artifact metadata, approval requests, and operator session view are all versioned schemas.
