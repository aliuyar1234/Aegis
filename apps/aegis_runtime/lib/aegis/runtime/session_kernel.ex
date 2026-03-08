defmodule Aegis.Runtime.SessionKernel do
  @moduledoc """
  Authoritative per-session state owner.

  `SessionKernel` is the first child in the Phase 01 session tree and is the only
  process allowed to advance authoritative session state in memory.
  """

  use GenServer

  alias Aegis.Leases
  alias Aegis.Runtime.{CommandHandler, Naming, SessionState}

  @component :session_kernel

  @spec start_link(map() | keyword()) :: GenServer.on_start()
  def start_link(session_attrs) do
    session_id =
      session_attrs
      |> Map.new()
      |> Map.fetch!(:session_id)

    GenServer.start_link(__MODULE__, session_attrs, name: Naming.via(session_id, @component))
  end

  @spec dispatch(String.t(), term(), keyword()) :: {:ok, map()} | {:error, term()}
  def dispatch(session_id, command, opts \\ []) do
    GenServer.call(Naming.via(session_id, @component), {:dispatch, command, opts})
  end

  @spec snapshot(String.t()) :: SessionState.t()
  def snapshot(session_id), do: GenServer.call(Naming.via(session_id, @component), :snapshot)

  @spec projection(String.t()) :: map()
  def projection(session_id), do: GenServer.call(Naming.via(session_id, @component), :projection)

  @spec adopt(String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def adopt(session_id, attrs) do
    GenServer.call(Naming.via(session_id, @component), {:adopt, attrs})
  end

  @spec report_lease_ambiguity(String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def report_lease_ambiguity(session_id, attrs) do
    GenServer.call(Naming.via(session_id, @component), {:report_lease_ambiguity, attrs})
  end

  @spec lease(String.t()) :: {:ok, Aegis.Leases.SessionLease.t()} | {:error, term()}
  def lease(session_id), do: GenServer.call(Naming.via(session_id, @component), :lease)

  @spec register_component(String.t(), atom(), pid()) :: :ok
  def register_component(session_id, component, pid)
      when is_binary(session_id) and is_atom(component) and is_pid(pid) do
    GenServer.cast(Naming.via(session_id, @component), {:register_component, component, pid})
  end

  @impl true
  def init(session_attrs) do
    session_attrs = Map.new(session_attrs)

    with {:ok, state, bootstrapping?} <- restore_or_initialize_state(session_attrs),
         {:ok, lease} <- ensure_runtime_lease(state, bootstrapping?),
         {:ok, state} <- finalize_init_state(state, lease, bootstrapping?) do
      {:ok, state}
    else
      {:error, reason} -> {:stop, reason}
    end
  end

  @impl true
  def handle_call({:dispatch, command, opts}, _from, state) do
    with {:ok, lease} <- Leases.authorize_command(state.durable.session_id, dispatch_lease_opts(state, opts)),
         state = put_lease(state, lease),
         {:ok, next_state, events} <- CommandHandler.handle(state, command, command_metadata(opts)) do
      persisted_state = persist!(next_state, events, append_metadata(opts))
      persisted_events = Aegis.Events.events(persisted_state.durable.session_id)

      {:reply, {:ok, reply_payload(persisted_state, persisted_events, lease)}, persisted_state}
    else
      {:error, reason} ->
        {:reply, {:error, reason}, state}
    end
  end

  def handle_call({:adopt, attrs}, _from, state) do
    attrs =
      attrs
      |> Map.new()
      |> Map.put_new(:tenant_id, state.durable.tenant_id)
      |> Map.put_new(:workspace_id, state.durable.workspace_id)
      |> Map.put_new(:lease_epoch, state.durable.lease_epoch)

    case Leases.adopt(state.durable.session_id, attrs, owner_node: Map.get(attrs, :owner_node, state.durable.owner_node)) do
      {:ok, lease} ->
        state = put_lease(state, lease)

        case CommandHandler.handle(state, {:adopt, attrs}, %{}) do
          {:ok, next_state, events} ->
            persisted_state = persist!(next_state, events, [])
            persisted_events = Aegis.Events.events(persisted_state.durable.session_id)

            {:reply, {:ok, reply_payload(persisted_state, persisted_events, lease)}, persisted_state}

          {:error, reason} ->
            {:reply, {:error, reason}, state}
        end

      {:error, reason} ->
        {:reply, {:error, reason}, state}
    end
  end

  def handle_call({:report_lease_ambiguity, attrs}, _from, state) do
    attrs =
      attrs
      |> Map.new()
      |> Map.put_new(:owner_node, state.durable.owner_node)
      |> Map.put_new(:lease_epoch, state.durable.lease_epoch)

    case Leases.mark_ambiguous(state.durable.session_id, attrs) do
      {:ok, lease} ->
        state = put_lease(state, lease)

        case CommandHandler.handle(state, {:report_lease_ambiguity, attrs}, %{}) do
          {:ok, next_state, events} ->
            persisted_state = persist!(next_state, events, [])
            persisted_events = Aegis.Events.events(persisted_state.durable.session_id)

            {:reply, {:ok, reply_payload(persisted_state, persisted_events, lease)}, persisted_state}

          {:error, reason} ->
            {:reply, {:error, reason}, state}
        end

      {:error, reason} ->
        {:reply, {:error, reason}, state}
    end
  end

  def handle_call(:lease, _from, state) do
    case Leases.current(state.durable.session_id) do
      {:ok, lease} -> {:reply, {:ok, lease}, put_lease(state, lease)}
      {:error, reason} -> {:reply, {:error, reason}, state}
    end
  end

  def handle_call(:snapshot, _from, state), do: {:reply, state, state}
  def handle_call(:projection, _from, state), do: {:reply, SessionState.projection(state), state}

  @impl true
  def handle_cast({:register_component, component, pid}, state) do
    {:noreply, SessionState.register_component(state, component, pid)}
  end

  defp restore_or_initialize_state(session_attrs) do
    session_id = Map.fetch!(session_attrs, :session_id)

    case Aegis.Events.hydrate(session_id) do
      {:ok, %{replay_state: replay_state}} ->
        {:ok, state_from_replay(session_attrs, replay_state), false}

      {:error, :unknown_session} ->
        {:ok, SessionState.new(session_attrs), true}

      {:error, reason} ->
        {:error, reason}
    end
  end

  defp ensure_runtime_lease(state, true) do
    case Leases.claim(SessionState.durable_snapshot(state), owner_node: state.durable.owner_node) do
      {:ok, lease} when lease.owner_node == state.durable.owner_node and lease.lease_status == :active ->
        {:ok, lease}

      {:ok, lease} ->
        {:error, {:lease_unavailable_for_bootstrap, lease}}

      {:error, reason} ->
        {:error, reason}
    end
  end

  defp ensure_runtime_lease(state, false) do
    case Leases.current(state.durable.session_id) do
      {:ok, lease} ->
        if lease.lease_status == :active and lease.owner_node != state.durable.owner_node do
          {:error, {:lease_held_by_other_owner, lease}}
        else
          {:ok, lease}
        end

      {:error, :missing_lease} ->
        Leases.claim(SessionState.durable_snapshot(state), owner_node: state.durable.owner_node)

      {:error, reason} ->
        {:error, reason}
    end
  end

  defp finalize_init_state(state, lease, true) do
    state = put_lease(state, lease)
    {:ok, next_state, events} = CommandHandler.bootstrap(state, %{})
    {:ok, persist!(next_state, events, [])}
  end

  defp finalize_init_state(state, lease, false) do
    {:ok, put_lease(state, lease)}
  end

  defp persist!(state, events, opts) do
    {:ok, result} = Aegis.Events.append(SessionState.durable_snapshot(state), events, opts)

    state
    |> SessionState.put_durable(%{
      last_seq_no: result.last_seq_no,
      latest_checkpoint_id:
        if(result.checkpoint,
          do: result.checkpoint.checkpoint_id,
          else: state.durable.latest_checkpoint_id
        )
    })
    |> SessionState.refresh_projection()
  end

  defp state_from_replay(session_attrs, replay_state) do
    state =
      SessionState.new(%{
        session_id: replay_state.session_id,
        tenant_id: replay_state.tenant_id,
        workspace_id: replay_state.workspace_id,
        session_kind: replay_state.session_kind,
        requested_by: replay_state.requested_by,
        owner_node: Map.get(session_attrs, :owner_node, replay_state.owner_node),
        control_mode: to_runtime_atom(replay_state.control_mode)
      })

    state
    |> SessionState.put_durable(%{
      session_kind: replay_state.session_kind,
      requested_by: replay_state.requested_by,
      owner_node: replay_state.owner_node,
      phase: to_runtime_atom(replay_state.phase),
      control_mode: to_runtime_atom(replay_state.control_mode),
      health: to_runtime_atom(replay_state.health),
      wait_reason: to_runtime_atom(replay_state.wait_reason),
      lease_epoch: replay_state.lease_epoch,
      last_seq_no: replay_state.last_seq_no,
      latest_checkpoint_id: replay_state.latest_checkpoint_id,
      latest_recovery_reason: replay_state.latest_recovery_reason,
      deadlines: replay_state.deadlines,
      pending_approvals: replay_state.pending_approvals,
      action_ledger: replay_state.action_ledger,
      child_agents: replay_state.child_agents,
      browser_handles: replay_state.browser_handles,
      summary_capsule: replay_state.summary_capsule,
      artifact_ids: replay_state.artifact_ids,
      recent_artifacts: replay_state.recent_artifacts,
      fenced: replay_state.fenced
    })
    |> SessionState.refresh_projection()
  end

  defp put_lease(state, lease) do
    state
    |> SessionState.put_durable(%{
      owner_node: lease.owner_node,
      lease_epoch: lease.lease_epoch
    })
    |> SessionState.refresh_projection()
  end

  defp dispatch_lease_opts(state, opts) do
    opts
    |> Keyword.new()
    |> Keyword.put_new(:owner_node, state.durable.owner_node)
    |> Keyword.put_new(:lease_epoch, state.durable.lease_epoch)
  end

  defp append_metadata(opts) do
    opts
    |> Keyword.new()
    |> Keyword.take([:actor_kind, :actor_id])
    |> Keyword.put_new(:actor_kind, "system")
    |> Keyword.put_new(:actor_id, "session_kernel")
  end

  defp command_metadata(opts) do
    opts
    |> Keyword.new()
    |> Enum.into(%{})
    |> Map.take([:command_id, :correlation_id, :causation_id, :trace_id, :span_id, :idempotency_key])
  end

  defp reply_payload(state, events, lease) do
    %{
      durable: SessionState.durable_snapshot(state),
      projection: SessionState.projection(state),
      events: events,
      lease: lease
    }
  end

  defp to_runtime_atom(value) when is_atom(value), do: value
  defp to_runtime_atom(value) when is_binary(value), do: String.to_existing_atom(value)
end
