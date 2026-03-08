# Local evaluation stack

This stack is the official local evaluation deployment path for Aegis. It is the
supported first environment for a fresh clone, smoke validation, and golden-path
exercise work before moving to larger deployment tracks.

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
make eval-up
make eval-init
make eval-check
make local-logs
make eval-down
```

`make eval-up` starts the stack. `make eval-init` initializes NATS, MinIO, and the
development/test Postgres databases. `make eval-check` validates that the official
fresh-clone onboarding and deployment surfaces are still coherent.

Compatibility aliases:

- `make local-up` -> `make eval-up`
- `make local-init` -> `make eval-init`
- `make local-down` -> `make eval-down`
- `make local-logs` -> streaming logs for the same stack

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

This stack is for evaluation, smoke validation, and first-clone onboarding only.
It is not the production deployment path.


## Heartbeats

- Worker registry heartbeats live on `aegis.v1.registry.heartbeat.{worker_kind}`.
- In-flight execution heartbeats live on `aegis.v1.event.heartbeat.{worker_kind}`.

Do not collapse these into one concept during implementation.
