# Patchlog V2

This file summarizes the v2 remediation pass.

## Major changes

- Fixed execution state so PHASE-00 is complete and PHASE-01 is the current start point.
- Added `meta/current-phase.yaml` and made task selection phase-aware.
- Repaired phase ordering and removed backward unlocks.
- Split browser baseline work from effectful browser mutation flows.
- Added explicit transport topology docs and machine-readable topology.
- Added per-event payload schemas, checkpoint schema, and event-to-schema mapping.
- Added operator/session/security schemas and stronger Protobuf contracts.
- Replaced prose-only phase-gate artifacts with YAML specs plus `scripts/run_phase_gate.py`.
- Added codegen config (`buf.yaml`, `buf.gen.yaml`, `scripts/generate_contracts.sh`).
- Strengthened validators for links, phase graph, schema coverage, traceability, and generated-file freshness.
- Added local stack init for MinIO bucket creation and NATS stream setup, and fixed OTEL -> Jaeger wiring.
- Deepened later phases 10–13 with stronger acceptance criteria, tests, and deliverables.
- Added machine-readable role, attribute, dangerous-action, operator-surface, and failure-runbook catalogs.
- Added browser wedge fixtures for read-only, effectful, and uncertainty scenarios.

## Tradeoffs

- Local validators fall back to structural Protobuf checks when `buf` is not installed, while CI is configured to use `buf` directly.
- The repository ships scaffold tests and fixtures rather than a full running implementation; that is intentional because this repo is the implementation harness, not the product itself.
