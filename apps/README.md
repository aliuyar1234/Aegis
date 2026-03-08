# apps/

This directory is reserved for Elixir umbrella applications.

## Boundary rules

- `aegis_runtime` owns live session truth.
- `aegis_leases` owns ownership semantics.
- `aegis_events` owns append/replay semantics.
- `aegis_gateway` owns API/UI entry points but never bypasses runtime APIs.
- `aegis_projection` owns read models, not canonical state.
- `aegis_execution_bridge` owns transport-facing dispatch from committed intent, worker registry liveness, and execution-attempt metadata in bridge-owned tables only.

Create code in these app boundaries rather than in a single monolith.
