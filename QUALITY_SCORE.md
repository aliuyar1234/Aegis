# QUALITY_SCORE.md

Aegis uses an explicit quality rubric so implementation work does not drift into “it compiles, ship it.”

## Passing bar

- **Per task:** no critical architecture or security regressions; linked tests and acceptance items updated.
- **Per phase:** weighted quality score **>= 85/100** and all required acceptance criteria met.
- **Public-demo readiness:** weighted quality score **>= 92/100** on phases 00–08.

## Weighted rubric

| Category | Weight | What good looks like |
|---|---:|---|
| Architecture alignment | 20 | Respects ADRs, invariants, service boundaries, and ownership model |
| Correctness and recovery | 20 | Handles failure semantics honestly; no silent unsafe behavior |
| Contracts and schema discipline | 10 | Runtime messages and tool schemas are explicit and versioned |
| Test coverage of important things | 15 | Replay, leases, policy, chaos, and demos are covered |
| Observability and operator legibility | 10 | Session state, timeline, health, and interventions are inspectable |
| Security and governance | 10 | Capability scoping, authz, dangerous actions, and audit are respected |
| Documentation and traceability | 10 | Tasks, ADR links, acceptance, and traceability remain synchronized |
| Cleanup / slop resistance | 5 | No drift phrases, no unused abstractions, no hidden authority |

## Scoring questions

For every major change, reviewers should ask:

1. Does this preserve session primacy?
2. Could this create a second source of truth?
3. Does this weaken replay, audit, or recovery?
4. Does this bypass policy or operator control?
5. Does this make Elixir incidental?
6. Does this push heavy work back onto the BEAM?
7. Did the relevant docs and traceability metadata get updated?
8. Did the right tests get added or changed?

## Hard fails regardless of score

The following are automatic failures:

- worker direct write path into canonical runtime tables
- side effects before commit/outbox
- no lease/fencing enforcement for authoritative owner
- no event or approval audit for effectful actions
- replay model that re-executes nondeterministic work by default
- hidden dangerous browser writes without policy/approval treatment

See `meta/quality-rubric.yaml` for the machine-readable version.
