defmodule Aegis.Runtime.SessionChild do
  @moduledoc false

  defmacro __using__(opts) do
    component = Keyword.fetch!(opts, :component)
    title = Keyword.fetch!(opts, :title)
    responsibility = Keyword.fetch!(opts, :responsibility)
    owns = Keyword.fetch!(opts, :owns)
    owns_lines = Enum.map_join(owns, "\n", &"- #{&1}")

    quote bind_quoted: [
            component: component,
            title: title,
            responsibility: responsibility,
            owns_lines: owns_lines
          ] do
      use GenServer

      alias Aegis.Runtime.{Naming, SessionKernel}

      @component component
      @moduledoc """
      #{title} is an ephemeral per-session child in the locked Phase 01 runtime tree.

      Responsibility:
      #{responsibility}

      Owns only ephemeral state:
      #{owns_lines}

      Canonical session truth stays in `Aegis.Runtime.SessionKernel`.
      """

      def start_link(session_id) do
        GenServer.start_link(__MODULE__, session_id, name: Naming.via(session_id, @component))
      end

      def init(session_id) do
        SessionKernel.register_component(session_id, @component, self())
        {:ok, %{session_id: session_id, component: @component}}
      end

      def snapshot(session_id), do: GenServer.call(Naming.via(session_id, @component), :snapshot)

      def handle_call(:snapshot, _from, state), do: {:reply, state, state}
    end
  end
end

defmodule Aegis.Runtime.ParticipantBridge do
  use Aegis.Runtime.SessionChild,
    component: :participant_bridge,
    title: "ParticipantBridge",
    responsibility:
      "Tracks operator and participant attachments without owning authoritative session fields.",
    owns: ["Presence metadata", "socket and channel references"]
end

defmodule Aegis.Runtime.TimerManager do
  use Aegis.Runtime.SessionChild,
    component: :timer_manager,
    title: "TimerManager",
    responsibility: "Owns live timer references for short waits and retry wakeups.",
    owns: [
      "in-process timer references",
      "timer scheduling metadata derived from durable deadlines"
    ]
end

defmodule Aegis.Runtime.CheckpointWorker do
  use Aegis.Runtime.SessionChild,
    component: :checkpoint_worker,
    title: "CheckpointWorker",
    responsibility: "Owns checkpoint trigger bookkeeping before PHASE-02 persistence exists.",
    owns: ["checkpoint scheduling state", "in-memory checkpoint trigger context"]
end

defmodule Aegis.Runtime.ToolRouter do
  use Aegis.Runtime.SessionChild,
    component: :tool_router,
    title: "ToolRouter",
    responsibility: "Owns ephemeral execution handles and worker callback correlation only.",
    owns: ["execution handles", "worker heartbeat references"]
end

defmodule Aegis.Runtime.PolicyCoordinator do
  use Aegis.Runtime.SessionChild,
    component: :policy_coordinator,
    title: "PolicyCoordinator",
    responsibility: "Coordinates policy checks without becoming the policy source of truth.",
    owns: ["policy request correlation", "pending policy evaluation refs"]
end

defmodule Aegis.Runtime.EventFanout do
  use Aegis.Runtime.SessionChild,
    component: :event_fanout,
    title: "EventFanout",
    responsibility: "Owns local event fan-out state for projections and subscribers.",
    owns: ["subscriber refs", "ephemeral event delivery bookkeeping"]
end

defmodule Aegis.Runtime.ArtifactCoordinator do
  use Aegis.Runtime.SessionChild,
    component: :artifact_coordinator,
    title: "ArtifactCoordinator",
    responsibility:
      "Owns signed-upload handoffs and attachment confirmations without storing blobs.",
    owns: ["artifact upload handoff state", "in-flight artifact confirmations"]
end

defmodule Aegis.Runtime.ChildAgentSupervisor do
  @moduledoc """
  Dynamic supervisor for logical child-agent processes inside a session.

  Child agents remain subordinate to `SessionKernel` and may not advance
  authoritative session state directly.
  """

  use DynamicSupervisor

  alias Aegis.Runtime.{Naming, SessionKernel}

  @component :child_agent_supervisor

  def start_link(session_id) do
    DynamicSupervisor.start_link(__MODULE__, session_id, name: Naming.via(session_id, @component))
  end

  @impl true
  def init(session_id) do
    SessionKernel.register_component(session_id, @component, self())
    DynamicSupervisor.init(strategy: :one_for_one)
  end
end
