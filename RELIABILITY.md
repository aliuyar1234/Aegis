# RELIABILITY.md

Aegis matters only if it behaves correctly under failure.

## Reliability doctrine

- Correctness beats availability on ownership ambiguity.
- Side effects must never be silently duplicated.
- Uncertainty must be surfaced explicitly, not hidden behind retries.
- Historical replay must remain possible after recovery.
- Operators must be able to understand failure from the timeline and runbooks.

## Machine-readable sources

- invariants: `meta/invariants.yaml`
- failures -> runbooks: `meta/failure-runbooks.yaml`
- acceptance criteria: `meta/acceptance-criteria.yaml`
- phase gates: `tests/phase-gates/*.yaml`

## Major failure classes

| Failure | Detection | Containment | Recovery doctrine |
|---|---|---|---|
| Python worker crash | heartbeat timeout / missing completion | current action | retry if safe; otherwise mark uncertain and escalate |
| Rust sidecar crash | sidecar heartbeat / stream failure | local hot path | restart sidecar, reattach, or degrade feature |
| BEAM process crash | OTP exit | process tree | restart child or rebuild session from checkpoint + tail |
| Node loss | lease renewal failure / expiry | all sessions on node | adopt on new node, hydrate, resume safely |
| Lease ambiguity | renewal uncertainty | current owner fenced | stop dispatch, surface degraded mode, allow adoption |
| External API timeout | deadline expiry | current action | classify transient vs uncertain side effect |
| Duplicate completion | duplicate execution_id or action terminal event | current action | dedupe, ledger, compensate/escalate if needed |
| Browser instability | page crash / disconnect / drift | browser action lane | reattach, restabilize, re-navigate, or hand to operator |
| Approval timeout | timer fire | approval wait | auto-deny/escalate per policy |
| Event corruption | hash mismatch / seq gap / replay failure | session | quarantine immediately |

## Guarantees

Aegis does offer:
- per-session total order
- append-only durable session timeline
- atomic commit of event + outbox intent
- checkpoint-plus-tail recovery
- single-owner semantics with fencing
- at-least-once transport with explicit dedupe strategy
- operator-visible uncertainty and recovery events

Aegis does not offer:
- global total order
- universal exactly-once external side effects
- perfect reconstruction of external world state
- autonomous progress during canonical datastore outage

## Runbook index

See `docs/runbooks/` and `meta/failure-runbooks.yaml`.
