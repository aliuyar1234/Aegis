# Internal runtime credibility demo

## Goal
Prove the runtime survives failure without hiding uncertainty or corrupting session truth.

## Fixtures and evidence
- `tests/browser_e2e/fixtures/read_only_account_lookup.yaml`
- `tests/browser_e2e/fixtures/uncertain_submit_recovery.yaml`
- `docs/runbooks/duplicate-execution.md`
- `docs/runbooks/event-corruption-quarantine.md`

## Flow
1. Start a session and confirm `session.created`, `session.owned`, and `checkpoint.created`.
2. Dispatch the read-only browser wedge and confirm `action.dispatched` plus `artifact.registered`.
3. Trigger a worker-loss or duplicate-terminal scenario and confirm `system.worker_lost`, `health.degraded`, or explicit uncertainty.
4. Hydrate from checkpoint plus replay and confirm the session resumes or lands in quarantined state instead of silently continuing.
5. Open replay and confirm artifacts and recovery markers are visible without external re-execution.

## Acceptance artifacts
- checkpoint evidence before external work
- degraded/quarantined recovery markers
- duplicate or uncertain write evidence in replay
- browser snapshot or artifact evidence in historical replay
