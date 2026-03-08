# Operations

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
make eval-up
make eval-init
make eval-check
make eval-down
```

Compatibility aliases remain available through `make local-up`, `make local-init`,
`make local-logs`, and `make local-down`.

The local stack is documented in `infra/local/README.md`.

## Launch readiness

Use:

```bash
make launch-check
make launch-ready
```

The customer-facing support and signoff surfaces are documented in `docs/operations/support.md`.

## Pre-customer launch proving

Use:

```bash
make prelaunch-check
make prelaunch-ready
```

The broader pre-customer launch surfaces are documented in:

- `docs/operations/launch-observability.md`
- `docs/operations/customer-environment-readiness.md`
- `docs/operations/customer-operations.md`

## Pilot operations

Use:

```bash
make pilot-check
make pilot-ready
```

The design-partner pilot execution, control-room, launch-exception, and exit-review
surfaces are documented in `docs/operations/pilot-operations.md`.

## GA transition

Use:

```bash
make ga-check
make ga-ready
```

The repeatable rollout, tenant-isolated production, service-scale support, and
GA transition surfaces are documented in:

- `docs/operations/customer-rollout.md`
- `docs/operations/service-scale-operations.md`
