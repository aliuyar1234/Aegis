# Can Change Later

These choices are important, but they are **not** core-thesis breakers. Keep them flexible unless or until a phase explicitly locks them down.

## Safe-to-change areas

- exact browser provider or hosting strategy
- local observability backend choice
- UI styling and presentation details
- deployment packaging details for dev environments
- analytics warehouse technology
- exact search backend beyond v1
- exact object-storage vendor
- whether some later connectors use MCP adapters

## Important note

“Can change later” does **not** mean “ignore now.” It means:

- keep interfaces clean
- avoid baking in unnecessary assumptions
- do not block core runtime work on these choices

## What this file does not permit

This file does **not** allow changing:

- session primacy
- single-owner semantics
- Postgres as source of truth
- append-only session timelines
- checkpoint + replay
- outbox before side effects
- JetStream as transport only
- browser-first wedge
- first-class operators and approvals

See `must-not-violate.md`.
