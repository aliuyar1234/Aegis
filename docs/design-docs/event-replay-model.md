# Event and replay model

This document defines the canonical event architecture for Aegis.

## Event doctrine

The session timeline is the system's authoritative history. It must be:

- append-only
- per-session totally ordered
- causally linked
- replayable
- compact enough to stay meaningful
- rich enough to reconstruct operator-facing truth

## Event categories

- `session.*`
- `agent.*`
- `observation.*`
- `action.*`
- `policy.*`
- `approval.*`
- `timer.*`
- `checkpoint.*`
- `artifact.*`
- `operator.*`
- `system.*`
- `health.*`

The registry lives in `schema/event-catalog/events.yaml`.

## Canonical envelope

See `schema/proto/aegis/runtime/v1/envelope.proto`.

Key fields:
- `event_id`
- `tenant_id`
- `workspace_id`
- `session_id`
- `seq_no`
- `type`
- `event_version`
- `occurred_at`
- `recorded_at`
- `actor_kind`
- `actor_id`
- `command_id`
- `correlation_id`
- `causation_id`
- `trace_id`
- `span_id`
- `lease_epoch`
- `idempotency_key`
- `determinism_class`
- `prev_event_hash`
- `event_hash`
- `payload`

## Ordering rules

- Total order is required **within a session**.
- Global total order is explicitly not a goal.
- `seq_no` is assigned by the authoritative SessionKernel owner.
- Unique index on `(session_id, seq_no)` enforces order in storage.

## Causality rules

Use:
- `command_id` to dedupe external requests and callbacks
- `correlation_id` to group causally related activity
- `causation_id` to point to the immediate parent event
- `trace_id` / `span_id` for distributed tracing continuity

## Idempotency rules

Idempotency exists at three layers:

1. **Command dedupe**
2. **Action execution dedupe**
3. **External side-effect idempotency or explicit uncertainty**

Aegis does not pretend to solve universal exactly-once semantics. It makes uncertainty explicit.

## Replay modes

### 1) Hydration replay
Used after crash, adoption, or restart. Load latest checkpoint, replay tail events, rebuild state.

### 2) Historical replay
Used by operators. Render events, statuses, artifacts, and approvals as they happened. No external re-execution.

### 3) Counterfactual replay (later)
Fork from a checkpoint and sandbox alternate decisions or model outputs. Not on the critical path.

## Deterministic vs nondeterministic boundaries

### Deterministic
- lifecycle transitions
- retry scheduling
- approval expiration
- policy outcomes for given inputs
- checkpoint loading
- projection rebuild

### Nondeterministic
- model outputs
- browser page state
- external API responses
- operator decisions
- wall-clock timing

Nondeterministic outputs must be captured as event payloads or artifacts.

See `docs/design-docs/replay-oracle.md` for the formal replay-equivalence and determinism
taxonomy added after the baseline replay model.

## Replay semantics for models and browsers

Historical replay never re-calls:
- model providers
- browser workers
- external APIs

Instead, it consumes:
- normalized result payloads
- raw output artifact refs
- recorded screenshots / DOM snapshots
- operator notes and approvals

## Example event sequence

Browser workflow: update customer billing address.

1. `session.created`
2. `session.owned`
3. `checkpoint.created`
4. `observation.received`
5. `agent.spawned`
6. `action.requested` (open browser)
7. `policy.evaluated` → allow
8. `action.dispatched`
9. `action.succeeded` (browser handle registered)
10. `artifact.registered` (initial screenshot)
11. `observation.browser_snapshot_added`
12. `agent.intent_emitted`
13. `action.requested` (login/navigate)
14. `policy.evaluated`
15. `action.dispatched`
16. `action.progressed`
17. `action.succeeded`
18. `checkpoint.created`
19. `action.requested` (mutate billing address)
20. `policy.evaluated` → require_approval
21. `approval.requested`
22. `session.waiting`
23. `operator.joined`
24. `approval.granted`
25. `session.mode_changed`
26. `action.dispatched`
27. `action.progressed`
28. `artifact.registered` (before-submit screenshot)
29. `action.succeeded`
30. `observation.browser_snapshot_added`
31. `action.requested` (verify)
32. `policy.evaluated`
33. `action.dispatched`
34. `action.succeeded`
35. `checkpoint.created`
36. `session.completed`

## Integrity model

Every event stores:
- `prev_event_hash`
- `event_hash`

Integrity checks should detect:
- seq gaps
- hash mismatches
- impossible causality
- schema/version mismatch during replay

When integrity fails, quarantine the session.


## Typed checkpoint contract

The checkpoint payload shape is locked by `schema/checkpoints/session-checkpoint-v1.schema.json`. Action ledger entries, approvals, deadlines, child agents, browser handles, and summary capsule fields are not implementation-defined.
