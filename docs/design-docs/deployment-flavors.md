# Deployment flavors

This document defines the packaging and deployment flavors introduced in PHASE-12.

## Goal

Make the self-hosted and managed packaging story explicit without forking the runtime model.

## Locked flavors

The machine-readable flavor catalog lives in `meta/deployment-flavors.yaml`.

The four locked flavors are:

- `oss_local`
- `shared_cloud`
- `isolated_execution`
- `dedicated_deployment`

## Flavor intent

### OSS local

- self-managed control plane
- shared worker pools
- local bucket or self-managed object store
- community-supported upgrade ownership

### Shared cloud

- managed shared control plane
- shared worker pools
- shared artifact bucket with tenant prefixes
- provider-managed rollout path

### Isolated execution

- managed shared control plane
- tenant-isolated execution pools
- tenant-dedicated artifact keyspace
- coordinated rollout because execution isolation is part of the promise

### Dedicated deployment

- dedicated control plane
- dedicated worker pools
- dedicated object-store boundary
- change-window upgrades with environment-specific coordination

## Invariants across all flavors

- the session runtime model does not fork by flavor
- PostgreSQL remains the source of truth
- JetStream remains transport, not truth
- operator surfaces still consume the same authoritative state model
- managed packaging may add operational services, but not alternate canonical state paths

## Packaging and upgrade consequence

Packaging differences exist to express ownership, isolation, and operational responsibility.
They do not create a second runtime architecture.

See:

- `docs/references/packaging-matrix.md`
- `docs/references/release-upgrade-matrix.md`
- `meta/split-release-policy.yaml`
