# Evaluation deployment

This document defines the official evaluation deployment path for Aegis.

## Intended use

Use this path for:

- fresh-clone onboarding
- local evaluation
- smoke validation
- golden-path exercise development
- architecture and operator walkthroughs

Do not treat this as the production deployment path.

## Required services

The official evaluation stack is the committed compose bundle in `infra/local/docker-compose.yml`.

It includes:

- PostgreSQL for canonical runtime truth
- NATS with JetStream for transport
- MinIO for artifact storage
- Jaeger for trace inspection
- OpenTelemetry Collector for local OTLP ingestion
- one-shot NATS bootstrap
- one-shot MinIO bucket bootstrap

## Official commands

```bash
make bootstrap
make eval-up
make eval-init
make eval-check
make smoke
```

## Required ports

- `5432` - PostgreSQL
- `4222` - NATS client
- `8222` - NATS monitoring
- `9000` - MinIO API
- `9001` - MinIO console
- `4317` - OTLP gRPC
- `4318` - OTLP HTTP
- `16686` - Jaeger UI

## Notes

- `make eval-up` is the official target name for the local evaluation stack.
- `make local-up` and related `local-*` commands remain compatibility aliases.
- `make eval-init` is responsible for service bootstrap and database initialization.
- `make eval-check` validates the committed onboarding and deployment surfaces before broader smoke validation.
