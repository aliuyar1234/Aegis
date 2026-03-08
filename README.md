# Aegis Runtime

Aegis Runtime is a BEAM-native durable control plane for long-lived AI sessions.
It is built to make browser-backed, failure-prone AI work operationally credible through durable ownership, replayable timelines, explicit policy boundaries, and strong operator control.

## Status

- Phases `00` through `13` are implemented in this repository.
- `PHASE-13` remains the terminal current marker because there is no `PHASE-14`.
- `make next-tasks` should report no unblocked tasks in the current roadmap.

## What Aegis Is

- A session-first runtime for long-lived AI work
- A control plane for orchestration, policy, approvals, replay, and recovery
- A BEAM-native backbone with Elixir owning truth, Python owning execution, and Rust owning hot-path sidecars
- A browser-operations-first system that treats operator intervention and uncertainty as first-class concerns

## Locked Thesis

- PostgreSQL is the source of truth
- Session timelines are append-only and event-sourced
- Checkpoints plus replay are mandatory
- Exactly one authoritative live owner exists per session
- Side effects launch only from committed intent via an outbox
- NATS JetStream is transport, not truth
- Operators and approvals are first-class runtime participants

## Start Here

1. [AGENTS.md](AGENTS.md)
2. [Product Definition](docs/overview/product.md)
3. [Architecture Overview](docs/overview/architecture.md)
4. [Current Phase](meta/current-phase.yaml)
5. [Implementation Order](docs/overview/implementation-order.md)
6. the active phase doc referenced by `meta/current-phase.yaml`
7. [Task Index](work-items/task-index.yaml)
8. [Test Strategy](docs/overview/test-strategy.md)
9. [Acceptance Criteria](docs/overview/acceptance-criteria.md)

## Repository Guide

- [Documentation index](docs/README.md)
- [Overview docs](docs/overview/)
- [Design docs](docs/design-docs/)
- [Execution plans](docs/exec-plans/active/)
- [Runbooks](docs/runbooks/)
- [Threat models](docs/threat-models/)
- [Schemas and contracts](schema/)
- [Task graph and phase slices](work-items/)

## Validation

Run these before shipping changes:

```bash
make validate
make ci
make next-tasks
make phase-gates
```

## Why This Repo Exists

This repository is more than source code. It is the implementation and architecture source of truth for Aegis:

- runtime and control-plane design
- phased execution plans and task graph
- machine-readable contracts and schemas
- validation, phase gates, and anti-drift checks

## Additional Navigation

- [Repository map](docs/overview/repo-map.md)
- [No-context survival checklist](docs/overview/no-context-survival.md)
- [Governance docs](docs/governance/)
- [Operations docs](docs/operations/)
- [Project docs](docs/project/)
