defmodule Aegis.Events do
  @moduledoc """
  Phase 02 boundary for append-only events, checkpoints, and replay.

  Source of truth:
  - phase doc: `docs/exec-plans/active/PHASE-02-events-checkpoints-replay.md`
  - ADRs: `docs/adr/0003-postgres-source-of-truth.md`,
    `docs/adr/0004-session-event-sourcing-depth.md`,
    `docs/adr/0005-checkpoint-strategy.md`,
    `docs/adr/0006-outbox-before-side-effects.md`
  - acceptance: `AC-008`, `AC-009`, `AC-010`, `AC-011`
  - tests: `TS-004` (`python3 scripts/run_elixir_suite.py TS-004`)

  Owns:
  - canonical event envelope construction and hash chaining
  - append + outbox atomicity inside the store transaction boundary
  - checkpoint serialization and restore helpers
  - replay for hydration and historical inspection
  - Postgres-backed persistence plus SQL migration artifacts
  """

  alias Aegis.Events.Store

  def reset!, do: Store.reset!()
  def append(session_state, events, opts \\ []), do: Store.append(session_state, events, opts)
  def events(session_id), do: Store.events(session_id)
  def latest_checkpoint(session_id), do: Store.latest_checkpoint(session_id)
  def checkpoints(session_id), do: Store.checkpoints(session_id)
  def outbox(session_id), do: Store.outbox(session_id)
  def historical_replay(session_id), do: Store.historical_replay(session_id)
  def hydrate(session_id), do: Store.hydrate(session_id)
  def schema_tables, do: Aegis.Events.Schema.tables()
end
