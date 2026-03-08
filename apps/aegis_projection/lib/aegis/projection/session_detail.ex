defmodule Aegis.Projection.SessionDetail do
  @moduledoc """
  Stable session-detail read model for Phase 06 operator inspection.

  This surface is derived from authoritative replay state plus checkpoint
  metadata and must not add UI-only state.
  """

  alias Aegis.Events
  alias Aegis.Runtime
  alias Aegis.Projection.RunbookLinks
  alias Aegis.Runtime.Projection

  @spec fetch(String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def fetch(session_id, scope \\ %{}) when is_binary(session_id) do
    with {:ok, replay} <- Runtime.historical_replay(session_id, scope) do
      projection = Projection.from_snapshot(replay.replay_state)
      checkpoints = Enum.map(Events.checkpoints(session_id, scope), &checkpoint_view/1)
      latest_checkpoint = if replay.latest_checkpoint, do: checkpoint_view(replay.latest_checkpoint), else: nil

      {:ok,
       %{
         session: projection,
         current_state: current_state_view(replay.replay_state, projection),
         summary_capsule: replay.replay_state.summary_capsule,
         child_agents: replay.replay_state.child_agents,
         browser_handles: replay.replay_state.browser_handles,
         browser_recovery: browser_recovery_view(replay.replay_state.browser_handles, projection),
         deadlines: projection.deadlines,
         approvals: projection.pending_approvals,
         in_flight_actions: projection.in_flight_actions,
         latest_checkpoint: latest_checkpoint,
         checkpoints: checkpoints,
         artifacts: artifact_views(replay.timeline, projection.recent_artifacts),
         controls: controls_for(projection),
         runbooks:
           RunbookLinks.for_timeline(
             "session-detail",
             replay.timeline,
             approval_wait: projection.wait_reason == "approval" or projection.pending_approvals != [],
             integrity_failure: Map.get(replay, :integrity_failure)
           )
       }}
    end
  end

  defp current_state_view(replay_state, projection) do
    %{
      session_kind: replay_state.session_kind,
      requested_by: replay_state.requested_by,
      isolation_tier: Map.get(replay_state, :isolation_tier, "tier_a"),
      owner_node: projection.owner_node,
      lease_epoch: projection.lease_epoch,
      phase: projection.phase,
      control_mode: projection.control_mode,
      health: projection.health,
      wait_reason: projection.wait_reason,
      fenced: projection.fenced,
      latest_recovery_reason: projection.latest_recovery_reason,
      latest_checkpoint_id: projection.latest_checkpoint_id,
      last_seq_no: projection.last_seq_no
    }
  end

  defp checkpoint_view(checkpoint) do
    %{
      checkpoint_id: checkpoint.checkpoint_id,
      seq_no: checkpoint.seq_no,
      inserted_at: checkpoint.inserted_at,
      phase: Map.get(checkpoint.payload, :phase),
      health: Map.get(checkpoint.payload, :health),
      wait_reason: Map.get(checkpoint.payload, :wait_reason),
      owner_node: Map.get(checkpoint.payload, :owner_node),
      lease_epoch: Map.get(checkpoint.payload, :lease_epoch)
    }
  end

  defp artifact_views(timeline, recent_artifacts) do
    recent_artifacts
    |> Enum.map(fn artifact ->
      registration =
        Enum.find(timeline, fn event ->
          event.type == "artifact.registered" and event.payload.artifact_id == artifact.artifact_id
        end)

      Map.merge(artifact, %{
        registered_seq_no: if(registration, do: registration.seq_no, else: nil),
        registered_at:
          if(registration, do: registration.recorded_at, else: Map.get(artifact, :recorded_at))
      })
    end)
    |> Enum.sort_by(fn artifact ->
      {-Map.get(artifact, :registered_seq_no, -1), artifact.artifact_id}
    end)
  end

  defp controls_for(projection) do
    %{
      join: true,
      add_note: true,
      pause: projection.phase in ["active", "waiting"] and projection.control_mode != "paused",
      abort: projection.phase in ["active", "waiting", "cancelling"],
      grant_approval: projection.pending_approvals != [],
      deny_approval: projection.pending_approvals != [],
      take_control:
        projection.phase in ["active", "waiting"] and projection.control_mode != "human_control",
      return_control:
        projection.control_mode in ["human_control", "paused"] or projection.wait_reason == "operator"
    }
  end

  defp browser_recovery_view([], _projection), do: nil

  defp browser_recovery_view(browser_handles, projection) do
    latest =
      browser_handles
      |> Enum.sort_by(fn handle ->
        {Map.get(handle, :last_observed_at, ""), Map.get(handle, :browser_handle_id, "")}
      end, :desc)
      |> List.first()

    %{
      browser_handle_id: Map.get(latest, :browser_handle_id),
      provider_kind: Map.get(latest, :provider_kind),
      page_ref: Map.get(latest, :page_ref),
      current_url: Map.get(latest, :current_url),
      state_ref: Map.get(latest, :state_ref),
      last_stable_artifact_id: Map.get(latest, :last_stable_artifact_id),
      restart_hint: Map.get(latest, :restart_hint),
      last_observed_at: Map.get(latest, :last_observed_at),
      degraded_reason:
        if(projection.health == "degraded" or projection.health == "quarantined",
          do: projection.latest_recovery_reason,
          else: nil
        )
    }
  end
end
