# Local development stack

This stack exists to support early runtime development and validation.

## Services

- PostgreSQL — canonical source of truth
- NATS with JetStream — cross-language transport
- MinIO — S3-compatible artifact storage
- OpenTelemetry collector — receives OTLP on `4317/4318`
- Jaeger — tracing UI on `16686`
- `nats-init` — one-shot stream/consumer bootstrap
- `minio-init` — one-shot bucket bootstrap

## Usage

```bash
make local-up
make local-init
make local-logs
make local-down
```

`make local-up` starts the stack. `make local-init` runs the init flow again if you reset local volumes.
The init flow also ensures the `aegis_test` database exists and reapplies the Phase 02 schema to both `aegis_dev` and `aegis_test`.

## Buckets and streams

- MinIO bucket: `aegis-artifacts`
- Streams: `ACTIONS`, `WORKER_EVENTS`, `WORKER_REGISTRY`

## Ports

- Postgres: `5432`
- NATS client: `4222`
- NATS monitoring: `8222`
- MinIO API: `9000`
- MinIO console: `9001`
- OTLP gRPC: `4317`
- OTLP HTTP: `4318`
- Jaeger UI: `16686`

This stack is for development and smoke validation only.


## Heartbeats

- Worker registry heartbeats live on `aegis.v1.registry.heartbeat.{worker_kind}`.
- In-flight execution heartbeats live on `aegis.v1.event.heartbeat.{worker_kind}`.

Do not collapse these into one concept during implementation.
