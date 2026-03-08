# Transport topology

This document is the prose explanation of `schema/transport-topology.yaml`.

## Boundary

JetStream is the **cross-language dispatch fabric**, not the source of truth. PostgreSQL remains authoritative.

## Stream model

- `ACTIONS` carries dispatch and cancel commands from the control plane to workers.
- `WORKER_EVENTS` carries accepted/progress/completed/failed/cancelled/heartbeat events from workers back to the control plane.
- `WORKER_REGISTRY` carries worker registration and worker heartbeats.

## Control-plane consumers

- `runtime-worker-events` is the explicit control-plane consumer for `aegis.v1.event.>` with explicit ack and bounded redelivery.
- `runtime-worker-registry` is the explicit control-plane consumer for `aegis.v1.registry.>` with explicit ack and bounded redelivery.

## Subject model

Subjects are explicit and versioned:
- `aegis.v1.registry.register.{worker_kind}`
- `aegis.v1.registry.heartbeat.{worker_kind}`
- `aegis.v1.command.dispatch.{worker_kind}`
- `aegis.v1.command.cancel.{worker_kind}`
- `aegis.v1.event.accepted.{worker_kind}`
- `aegis.v1.event.progress.{worker_kind}`
- `aegis.v1.event.completed.{worker_kind}`
- `aegis.v1.event.failed.{worker_kind}`
- `aegis.v1.event.cancelled.{worker_kind}`
- `aegis.v1.event.heartbeat.{worker_kind}`

## Routing and isolation

- `worker_kind` is the primary routing key.
- tenant/workspace/session/trace data travel in headers, not in subject names, for Tier A.
- higher isolation tiers may use dedicated streams or deployment namespaces without changing message contracts.

## Required headers

The transport header contract is explicit:
- `x-aegis-trace-id`
- `x-aegis-tenant-id`
- `x-aegis-workspace-id`
- `x-aegis-session-id`
- `x-aegis-lease-epoch`
- `x-aegis-contract-version`
- `x-aegis-isolation-tier`

## Ack and redelivery

- dispatch commands use explicit ack; a worker acks only after it has durably accepted an execution attempt.
- worker events are at-least-once; the SessionKernel deduplicates by `execution_id` and terminal status.
- registry and worker-event consumers nack malformed or unknown payloads and rely on bounded redelivery rather than silent drop.
- redelivery is bounded; repeated redelivery moves the session toward uncertainty or human escalation rather than silent retry.

## Size rules

JetStream messages carry structured metadata only. Large raw payloads, screenshots, DOM snapshots, traces, and large model outputs go through object storage and are referenced by artifact IDs.

## Timeouts and heartbeats

Timeout classes are defined in the topology file and referenced by tool descriptors. Heartbeats are expected every five seconds by default, with loss declared after three misses unless a tool descriptor overrides the class.


## Runtime heartbeats

Two heartbeat classes exist and must not be confused:

- `WorkerHeartbeat` on `aegis.v1.registry.heartbeat.{worker_kind}` reports worker liveness and available capacity to the registry.
- `ActionHeartbeat` on `aegis.v1.event.heartbeat.{worker_kind}` reports that a specific in-flight execution is still alive.

Registry heartbeats support scheduling. Action heartbeats support orphan detection and uncertain-side-effect handling. They are separate contracts on purpose.

## Cancel-path coverage

Cancel traffic is explicit and first-class. Each worker kind has its own cancel consumer in the local topology so the cancel path is not left to implementer inference.
