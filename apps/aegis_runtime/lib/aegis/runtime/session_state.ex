defmodule Aegis.Runtime.SessionState do
  @moduledoc """
  Authoritative Phase 01 session state split into durable and ephemeral sections.

  Durable state models what must survive checkpointing and replay.
  Ephemeral state models process-local attachments that should rebuild after crashes.
  """

  alias Aegis.Runtime.{Event, Projection}

  defmodule Durable do
    @moduledoc false

    @enforce_keys [:session_id, :tenant_id, :workspace_id]
    defstruct session_id: nil,
              tenant_id: nil,
              workspace_id: nil,
              session_kind: "browser_operation",
              requested_by: "system",
              owner_node: nil,
              phase: :provisioning,
              control_mode: :autonomous,
              health: :healthy,
              wait_reason: :none,
              lease_epoch: 0,
              last_seq_no: 0,
              latest_checkpoint_id: nil,
              latest_recovery_reason: nil,
              deadlines: [],
              pending_approvals: [],
              action_ledger: [],
              child_agents: [],
              browser_handles: [],
              summary_capsule: %{
                planner_summary: "",
                salient_facts: [],
                operator_notes: []
              },
              artifact_ids: [],
              recent_artifacts: [],
              fenced: false

    @type t :: %__MODULE__{
            session_id: String.t(),
            tenant_id: String.t(),
            workspace_id: String.t(),
            session_kind: String.t(),
            requested_by: String.t(),
            owner_node: String.t(),
            phase: Aegis.Runtime.SessionState.phase(),
            control_mode: Aegis.Runtime.SessionState.control_mode(),
            health: Aegis.Runtime.SessionState.health(),
            wait_reason: Aegis.Runtime.SessionState.wait_reason(),
            lease_epoch: non_neg_integer(),
            last_seq_no: non_neg_integer(),
            latest_checkpoint_id: String.t() | nil,
            latest_recovery_reason: String.t() | nil,
            deadlines: [map()],
            pending_approvals: [map()],
            action_ledger: [map()],
            child_agents: [map()],
            browser_handles: [map()],
            summary_capsule: map(),
            artifact_ids: [String.t()],
            recent_artifacts: [map()],
            fenced: boolean()
          }
  end

  defmodule Ephemeral do
    @moduledoc false

    defstruct recent_events: [],
              projection: %{},
              component_pids: %{},
              timer_refs: %{},
              sockets: %{},
              worker_heartbeats: %{},
              browser_attachments: %{},
              prompt_assembly_cache: %{}

    @type t :: %__MODULE__{
            recent_events: [Event.t()],
            projection: map(),
            component_pids: %{optional(atom()) => pid()},
            timer_refs: map(),
            sockets: map(),
            worker_heartbeats: map(),
            browser_attachments: map(),
            prompt_assembly_cache: map()
          }
  end

  @type phase :: :provisioning | :hydrating | :active | :waiting | :cancelling | :terminal
  @type control_mode :: :autonomous | :supervised | :human_control | :paused
  @type health :: :healthy | :degraded | :quarantined

  @type wait_reason ::
          :none
          | :action
          | :approval
          | :timer
          | :external_dependency
          | :operator
          | :lease_recovery

  @type t :: %__MODULE__{
          durable: Durable.t(),
          ephemeral: Ephemeral.t()
        }

  defstruct durable: nil, ephemeral: nil

  @required_identity [:session_id, :tenant_id, :workspace_id]

  @spec new(map() | keyword()) :: t()
  def new(attrs) do
    attrs = Map.new(attrs)

    Enum.each(@required_identity, fn key ->
      Map.fetch!(attrs, key)
    end)

    durable =
      struct!(Durable, %{
        session_id: attrs.session_id,
        tenant_id: attrs.tenant_id,
        workspace_id: attrs.workspace_id,
        session_kind: Map.get(attrs, :session_kind, "browser_operation"),
        requested_by: Map.get(attrs, :requested_by, "system"),
        owner_node: Map.get(attrs, :owner_node, Atom.to_string(node())),
        control_mode: Map.get(attrs, :control_mode, :autonomous)
      })

    %__MODULE__{durable: durable, ephemeral: %Ephemeral{}}
    |> refresh_projection()
  end

  @spec next_seq_no(t()) :: non_neg_integer()
  def next_seq_no(%__MODULE__{durable: durable}), do: durable.last_seq_no + 1

  @spec put_durable(t(), map()) :: t()
  def put_durable(%__MODULE__{durable: durable} = state, attrs) do
    %{state | durable: struct!(durable, Map.new(attrs))}
  end

  @spec apply_event(t(), Event.t()) :: t()
  def apply_event(%__MODULE__{} = state, %Event{} = event) do
    state
    |> put_durable(%{last_seq_no: event.seq_no})
    |> update_ephemeral(fn ephemeral ->
      %{ephemeral | recent_events: ephemeral.recent_events ++ [event]}
    end)
    |> refresh_projection()
  end

  @spec register_component(t(), atom(), pid()) :: t()
  def register_component(%__MODULE__{} = state, component, pid)
      when is_atom(component) and is_pid(pid) do
    update_ephemeral(state, fn ephemeral ->
      %{ephemeral | component_pids: Map.put(ephemeral.component_pids, component, pid)}
    end)
  end

  @spec durable_snapshot(t()) :: Durable.t()
  def durable_snapshot(%__MODULE__{durable: durable}), do: durable

  @spec ephemeral_snapshot(t()) :: Ephemeral.t()
  def ephemeral_snapshot(%__MODULE__{ephemeral: ephemeral}), do: ephemeral

  @spec projection(t()) :: map()
  def projection(%__MODULE__{ephemeral: ephemeral}), do: ephemeral.projection

  @spec events(t()) :: [Event.t()]
  def events(%__MODULE__{ephemeral: ephemeral}), do: ephemeral.recent_events

  @spec refresh_projection(t()) :: t()
  def refresh_projection(%__MODULE__{} = state) do
    projection = Projection.from_state(state)
    update_ephemeral(state, fn ephemeral -> %{ephemeral | projection: projection} end)
  end

  defp update_ephemeral(%__MODULE__{ephemeral: ephemeral} = state, fun) do
    %{state | ephemeral: fun.(ephemeral)}
  end
end
