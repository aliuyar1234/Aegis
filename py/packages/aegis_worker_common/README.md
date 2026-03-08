# aegis_worker_common

## Purpose
shared transport, tracing, schema, and capability-token helpers

## Must not do
- own authoritative session state
- write canonical runtime tables
- bypass capability tokens or policy decisions
