defmodule Aegis.Projection.SessionReplay do
  @moduledoc """
  Replay and timeline read model for Phase 06 operator historical inspection.

  The scrubber state is derived from recorded events and checkpoints rather than
  hidden UI caches.
  """

  alias Aegis.Events
  alias Aegis.Projection.RunbookLinks
  alias Aegis.Runtime
  alias Aegis.Runtime.Projection

  @spec fetch(String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def fetch(session_id, opts \\ []) when is_binary(session_id) do
    opts = Map.new(opts)

    with {:ok, replay} <- Runtime.historical_replay(session_id) do
      selected_seq_no = normalize_selected_seq_no(opts[:seq_no], replay.replay_state.last_seq_no)
      {:ok, selected} = Events.replay_at(session_id, selected_seq_no)
      checkpoints = Events.checkpoints(session_id)
      artifacts = build_artifact_index(replay.timeline, replay.replay_state.recent_artifacts)

      {:ok,
       %{
         session: Projection.from_snapshot(replay.replay_state),
         scrubber: %{
           min_seq_no: 0,
           max_seq_no: replay.replay_state.last_seq_no,
           selected_seq_no: selected_seq_no
         },
         selected_state: Projection.from_snapshot(selected.replay_state),
         selected_checkpoint:
           if(selected.latest_checkpoint, do: checkpoint_entry(selected.latest_checkpoint), else: nil),
         timeline: timeline_entries(replay.timeline, checkpoints, artifacts),
         checkpoints: Enum.map(checkpoints, &checkpoint_entry/1),
         artifacts: Map.values(artifacts) |> Enum.sort_by(&{-Map.get(&1, :registered_seq_no, -1), &1.artifact_id}),
         runbooks: RunbookLinks.for_timeline("replay", replay.timeline)
       }}
    end
  end

  @spec artifact_view(String.t(), String.t()) :: {:ok, map()} | {:error, term()}
  def artifact_view(session_id, artifact_id) when is_binary(session_id) and is_binary(artifact_id) do
    with {:ok, replay} <- Runtime.historical_replay(session_id) do
      artifacts = build_artifact_index(replay.timeline, replay.replay_state.recent_artifacts)

      case Map.get(artifacts, artifact_id) do
        nil -> {:error, :unknown_artifact}
        artifact -> {:ok, artifact}
      end
    end
  end

  defp timeline_entries(events, checkpoints, artifacts) do
    event_entries = Enum.map(events, &event_entry(&1, artifacts))
    checkpoint_entries = Enum.map(checkpoints, &checkpoint_entry/1)

    (event_entries ++ checkpoint_entries)
    |> Enum.sort_by(fn entry ->
      {entry.seq_no, entry_order(entry.entry_kind), Map.get(entry, :type, ""), Map.get(entry, :checkpoint_id, "")}
    end)
  end

  defp event_entry(event, artifacts) do
    %{
      entry_kind: "event",
      seq_no: event.seq_no,
      type: event.type,
      occurred_at: event.occurred_at,
      recorded_at: event.recorded_at,
      actor_kind: event.actor_kind,
      actor_id: event.actor_id,
      trace_id: event.trace_id,
      correlation_id: event.correlation_id,
      overlay_tags: overlay_tags(event),
      headline: headline(event),
      artifact_id: Map.get(event.payload, :artifact_id),
      artifact:
        if(event.type == "artifact.registered",
          do: Map.get(artifacts, Map.get(event.payload, :artifact_id)),
          else: nil
        )
    }
  end

  defp checkpoint_entry(checkpoint) do
    %{
      entry_kind: "checkpoint",
      type: "checkpoint.created",
      seq_no: checkpoint.seq_no,
      checkpoint_id: checkpoint.checkpoint_id,
      inserted_at: checkpoint.inserted_at,
      phase: Map.get(checkpoint.payload, :phase),
      health: Map.get(checkpoint.payload, :health),
      wait_reason: Map.get(checkpoint.payload, :wait_reason),
      overlay_tags: ["checkpoint"],
      headline: "Checkpoint created"
    }
  end

  defp build_artifact_index(timeline, recent_artifacts) do
    artifact_events =
      timeline
      |> Enum.filter(&(&1.type == "artifact.registered"))
      |> Enum.map(fn event ->
        {
          event.payload.artifact_id,
          %{
            artifact_id: event.payload.artifact_id,
            artifact_kind: event.payload.artifact_kind,
            sha256: event.payload.sha256,
            content_type: event.payload.content_type,
            size_bytes: event.payload.size_bytes,
            retention_class: event.payload.retention_class,
            redaction_state: event.payload.redaction_state,
            storage_ref: Map.get(event.payload, :storage_ref),
            recorded_at: Map.get(event.payload, :recorded_at),
            action_id: Map.get(event.payload, :action_id),
            registered_seq_no: event.seq_no,
            registered_at: event.recorded_at
          }
        }
      end)
      |> Enum.into(%{})

    Enum.reduce(recent_artifacts, artifact_events, fn artifact, acc ->
      Map.update(acc, artifact.artifact_id, artifact, &Map.merge(artifact, &1))
    end)
  end

  defp overlay_tags(event) do
    []
    |> maybe_tag(String.starts_with?(event.type, "operator."), "operator")
    |> maybe_tag(String.starts_with?(event.type, "approval."), "approval")
    |> maybe_tag(event.type == "policy.evaluated", "policy")
    |> maybe_tag(event.type == "artifact.registered", "artifact")
    |> maybe_tag(event.type in ["session.waiting", "session.resumed"], "wait")
    |> maybe_tag(event.type in ["system.lease_lost", "system.node_recovered"], "recovery")
    |> maybe_tag(event.type in ["health.degraded", "session.quarantined"], "health")
  end

  defp headline(%{type: "session.waiting", payload: payload}),
    do: "Session waiting: #{Map.get(payload, :reason, "unknown")}"

  defp headline(%{type: "approval.requested", payload: payload}),
    do: "Approval requested for #{payload.action_id}"

  defp headline(%{type: "approval.granted", payload: payload}),
    do: "Approval granted for #{payload.action_id}"

  defp headline(%{type: "approval.denied", payload: payload}),
    do: "Approval denied for #{payload.action_id}"

  defp headline(%{type: "approval.expired", payload: payload}),
    do: "Approval expired for #{payload.action_id}"

  defp headline(%{type: "policy.evaluated", payload: payload}),
    do: "Policy decision: #{payload.decision} for #{payload.action_id}"

  defp headline(%{type: "artifact.registered", payload: payload}),
    do: "Artifact registered: #{payload.artifact_kind}"

  defp headline(%{type: "action.requested", payload: payload}),
    do: "Action requested: #{payload.tool_id}"

  defp headline(%{type: "action.succeeded", payload: payload}),
    do: "Action succeeded: #{payload.action_id}"

  defp headline(%{type: "action.failed", payload: payload}),
    do: "Action failed: #{payload.action_id}"

  defp headline(%{type: "system.node_recovered"}),
    do: "Session recovered"

  defp headline(%{type: "system.lease_lost"}),
    do: "Lease lost"

  defp headline(%{type: "operator.joined", payload: payload}),
    do: "Operator joined: #{payload.operator_id}"

  defp headline(%{type: "operator.note_added", payload: payload}),
    do: "Operator note added: #{payload.note_ref}"

  defp headline(%{type: "operator.paused", payload: payload}),
    do: "Operator paused session: #{payload.reason}"

  defp headline(%{type: "operator.abort_requested", payload: payload}),
    do: "Operator abort requested: #{payload.reason}"

  defp headline(%{type: "operator.took_control", payload: payload}),
    do: "Operator took control: #{payload.operator_id}"

  defp headline(%{type: "operator.returned_control", payload: payload}),
    do: "Operator returned control: #{payload.return_context}"

  defp headline(event), do: event.type

  defp normalize_selected_seq_no(nil, max_seq_no), do: max_seq_no

  defp normalize_selected_seq_no(seq_no, max_seq_no) when is_integer(seq_no) do
    seq_no
    |> max(0)
    |> min(max_seq_no)
  end

  defp entry_order("event"), do: 0
  defp entry_order("checkpoint"), do: 1

  defp maybe_tag(tags, true, tag), do: tags ++ [tag]
  defp maybe_tag(tags, false, _tag), do: tags
end
