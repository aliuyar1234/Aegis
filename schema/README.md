# schema/

This directory contains the machine-readable contract surface for Aegis.

## Subdirectories

- `proto/` — runtime control-plane / execution-plane contracts
- `jsonschema/` — tool I/O, operator-facing payloads, artifact metadata, and security payloads
- `event-catalog/` — event registry and event-to-schema mapping
- `event-payloads/` — typed per-event payload schemas
- `checkpoints/` — checkpoint schemas
- `transport-topology.yaml` — JetStream stream/subject/consumer topology

The schema directory is part of the SSOT, not documentation garnish.
