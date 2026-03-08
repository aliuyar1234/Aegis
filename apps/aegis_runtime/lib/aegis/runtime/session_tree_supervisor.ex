defmodule Aegis.Runtime.SessionTreeSupervisor do
  @moduledoc """
  Canonical per-session supervisor tree.

  Phase refs:
  - `P01-T03`
  - `AC-006`
  - `docs/design-docs/runtime-model.md`

  Strategy:
  - `:rest_for_one` so the authoritative `SessionKernel` remains first
  - if `SessionKernel` exits, dependent children rebuild around restored state
  - if a downstream child exits, the kernel can remain authoritative
  """

  use Supervisor

  alias Aegis.Runtime.{
    ArtifactCoordinator,
    CheckpointWorker,
    ChildAgentSupervisor,
    EventFanout,
    Naming,
    ParticipantBridge,
    PolicyCoordinator,
    SessionKernel,
    TimerManager,
    ToolRouter
  }

  @spec start_link(map() | keyword()) :: Supervisor.on_start()
  def start_link(session_attrs) do
    session_id = fetch_session_id!(session_attrs)

    Supervisor.start_link(__MODULE__, session_attrs, name: Naming.via(session_id, :session_tree))
  end

  @spec child_spec(map() | keyword()) :: Supervisor.child_spec()
  def child_spec(session_attrs) do
    session_id = fetch_session_id!(session_attrs)

    %{
      id: {__MODULE__, session_id},
      start: {__MODULE__, :start_link, [session_attrs]},
      type: :supervisor,
      restart: :permanent,
      shutdown: :infinity
    }
  end

  @impl true
  def init(session_attrs) do
    session_id = fetch_session_id!(session_attrs)

    children = [
      {SessionKernel, session_attrs},
      {ParticipantBridge, session_id},
      {TimerManager, session_id},
      {CheckpointWorker, session_id},
      {ToolRouter, session_id},
      {PolicyCoordinator, session_id},
      {ChildAgentSupervisor, session_id},
      {EventFanout, session_id},
      {ArtifactCoordinator, session_id}
    ]

    Supervisor.init(children, strategy: :rest_for_one)
  end

  defp fetch_session_id!(session_attrs) do
    session_attrs
    |> Map.new()
    |> Map.fetch!(:session_id)
  end
end
