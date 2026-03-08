defmodule Aegis.Runtime do
  @moduledoc """
  Runtime boundary for the authoritative session owner.

  Source of truth:
  - phase doc: `docs/exec-plans/active/PHASE-01-session-kernel.md`
  - ADRs: `docs/adr/0001-session-primary-abstraction.md`,
    `docs/adr/0005-checkpoint-strategy.md`
  - acceptance: `AC-005`, `AC-006`, `AC-007`, `AC-012`, `AC-013`, `AC-014`
  - tests: `TS-003` (`python3 scripts/run_elixir_suite.py TS-003`),
    `TS-005` (`python3 scripts/run_elixir_suite.py TS-005`)

  Owns:
  - `SessionKernel` and the canonical per-session supervisor tree
  - lifecycle transitions and wait-reason semantics
  - lease-gated command acceptance, self-fencing, and adoption entrypoints
  - durable vs ephemeral runtime state boundaries
  - projection shaping over authoritative session state before downstream UI work

  Must not own:
  - Postgres append/replay and outbox logic, which belongs to `aegis_events`
  - lease authority, which belongs to `aegis_leases`
  - JetStream dispatch, which belongs to `aegis_execution_bridge`
  - policy truth, which belongs to `aegis_policy`
  - operator read models as canonical state, which belongs to `aegis_projection`
  """

  alias Aegis.Runtime.{Naming, SessionHostSupervisor, SessionKernel}

  @spec start_session(map() | keyword()) :: DynamicSupervisor.on_start_child()
  def start_session(attrs), do: SessionHostSupervisor.start_session(attrs)

  @spec dispatch(String.t(), term(), keyword()) :: {:ok, map()} | {:error, term()}
  def dispatch(session_id, command, opts \\ []), do: SessionKernel.dispatch(session_id, command, opts)

  @spec adopt(String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def adopt(session_id, attrs), do: SessionKernel.adopt(session_id, attrs)

  @spec report_lease_ambiguity(String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def report_lease_ambiguity(session_id, attrs), do: SessionKernel.report_lease_ambiguity(session_id, attrs)

  @spec snapshot(String.t()) :: Aegis.Runtime.SessionState.t()
  def snapshot(session_id), do: SessionKernel.snapshot(session_id)

  @spec projection(String.t()) :: map()
  def projection(session_id), do: SessionKernel.projection(session_id)

  @spec lease(String.t()) :: {:ok, Aegis.Leases.SessionLease.t()} | {:error, term()}
  def lease(session_id), do: SessionKernel.lease(session_id)

  @spec events(String.t(), map() | keyword()) :: [Aegis.Events.Envelope.t()]
  def events(session_id, scope \\ %{}), do: Aegis.Events.events(session_id, scope)

  @spec historical_replay(String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def historical_replay(session_id, scope \\ %{}), do: Aegis.Events.historical_replay(session_id, scope)

  @spec hydrate(String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def hydrate(session_id, scope \\ %{}), do: Aegis.Events.hydrate(session_id, scope)

  @spec tree_pid(String.t()) :: pid() | nil
  def tree_pid(session_id), do: Naming.whereis(session_id, :session_tree)
end
