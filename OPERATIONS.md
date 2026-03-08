# OPERATIONS.md

Aegis is operated through timelines, projections, traces, and runbooks.

## Primary operator surfaces

- session fleet
- session detail
- approvals queue
- replay

The machine-readable surface map lives in `meta/operator-surfaces.yaml`.

## Required operational artifacts

- phase gates under `tests/phase-gates/`
- runbooks under `docs/runbooks/`
- transport topology under `schema/transport-topology.yaml`
- failure mapping under `meta/failure-runbooks.yaml`
- current phase state under `meta/current-phase.yaml`
- enterprise acceptance checklist under `meta/enterprise-acceptance-checklist.yaml`
- dedicated tenant evidence under `meta/dedicated-tenant-evidence.yaml`

## Local stack

Use:

```bash
make local-up
make local-init
make local-logs
make local-down
```

The local stack is documented in `infra/local/README.md`.
