# aegis_execution_bridge

## Purpose

Outbox consumers and transport bridge for the Phase 04 execution boundary.

## Responsibilities

- claim committed action intent from the Postgres outbox
- publish dispatch and cancel commands onto the locked transport subjects
- track worker registration, available capacity, and registry heartbeats
- persist execution-attempt state in bridge-owned tables
- ingest accept/progress/heartbeat/completion/failure/cancel callbacks
- detect accept-deadline expiry and missed action heartbeats
- detect hard-deadline expiry before execution attempts run forever
- preserve trace context and idempotency metadata across the bridge boundary
- run the control-plane transport consumer and background dispatch/timeout pollers

## Owned tables

- `worker_registrations`
- `action_executions`

## Must not own

- canonical session state, event ordering, checkpoints, or leases
- direct writes to `sessions`, `session_events`, `session_checkpoints`, `session_leases`, or `outbox`
- browser implementation details or tool-specific business logic

## Source of truth

- phase doc: `docs/exec-plans/active/PHASE-04-worker-contracts-transport.md`
- ADRs: `docs/adr/0007-nats-jetstream-transport.md`, `docs/adr/0008-protobuf-jsonschema-contracts.md`
- acceptance: `AC-015`, `AC-016`, `AC-017`, `AC-018`, `AC-019`
- tests: `TS-002`, `TS-006`, `TS-018`

## Main entrypoints

- `Aegis.ExecutionBridge`
- `Aegis.ExecutionBridge.Store`
- `Aegis.ExecutionBridge.TransportTopology`
- `Aegis.ExecutionBridge.Guardrails`
- `Aegis.ExecutionBridge.TransportConsumer`
- `Aegis.ExecutionBridge.Poller`
