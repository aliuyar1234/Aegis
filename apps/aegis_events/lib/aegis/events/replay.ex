defmodule Aegis.Events.Replay do
  @moduledoc false

  def initial_state(session_row) do
    %{
      tenant_id: session_row.tenant_id,
      workspace_id: session_row.workspace_id,
      session_id: session_row.session_id,
      session_kind: Map.get(session_row, :session_kind, "browser_operation"),
      requested_by: Map.get(session_row, :requested_by, "system"),
      owner_node: Map.get(session_row, :owner_node, Atom.to_string(node())),
      phase: "provisioning",
      control_mode: "autonomous",
      health: "healthy",
      wait_reason: "none",
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
    }
  end

  def from_checkpoint(nil, session_row), do: initial_state(session_row)

  def from_checkpoint(checkpoint, session_row) do
    payload = checkpoint.payload

    %{
      tenant_id: payload.tenant_id,
      workspace_id: payload.workspace_id,
      session_id: payload.session_id,
      session_kind:
        Map.get(payload, :session_kind, Map.get(session_row, :session_kind, "browser_operation")),
      requested_by:
        Map.get(payload, :requested_by, Map.get(session_row, :requested_by, "system")),
      owner_node:
        Map.get(payload, :owner_node, Map.get(session_row, :owner_node, Atom.to_string(node()))),
      phase: payload.phase,
      control_mode: payload.control_mode,
      health: payload.health,
      wait_reason: payload.wait_reason,
      lease_epoch: payload.lease_epoch,
      last_seq_no: checkpoint.seq_no,
      latest_checkpoint_id: payload.latest_checkpoint_id || checkpoint.checkpoint_id,
      latest_recovery_reason: payload.latest_recovery_reason,
      deadlines: payload.deadlines,
      pending_approvals: payload.pending_approvals,
      action_ledger: payload.action_ledger,
      child_agents: payload.child_agents,
      browser_handles: payload.browser_handles,
      summary_capsule: payload.summary_capsule,
      artifact_ids: payload.artifact_ids,
      recent_artifacts: Map.get(payload, :recent_artifacts, []),
      fenced: Map.get(payload, :fenced, false)
    }
  end

  def replay(session_row, checkpoint, events) do
    events
    |> Enum.reduce(from_checkpoint(checkpoint, session_row), &apply_event(&2, &1))
  end

  def apply_event(state, envelope) do
    state
    |> put_common(envelope)
    |> do_apply(envelope)
  end

  defp put_common(state, envelope) do
    state
    |> Map.put(:last_seq_no, envelope.seq_no)
  end

  defp do_apply(state, %{type: "session.created", payload: payload}) do
    state
    |> Map.put(:session_kind, payload.session_kind)
    |> Map.put(:requested_by, payload.requested_by)
  end

  defp do_apply(state, %{type: "session.hydrated", payload: payload}) do
    state
    |> Map.put(:phase, "hydrating")
    |> Map.put(:wait_reason, "none")
    |> Map.put(:owner_node, payload.owner_node)
    |> Map.put(:lease_epoch, payload.lease_epoch)
    |> Map.put(:latest_checkpoint_id, payload.restored_from_checkpoint_id)
  end

  defp do_apply(state, %{type: "session.owned", payload: payload}) do
    state
    |> Map.put(:phase, "active")
    |> Map.put(:wait_reason, "none")
    |> Map.put(:health, "healthy")
    |> Map.put(:owner_node, payload.owner_node)
    |> Map.put(:lease_epoch, payload.lease_epoch)
    |> Map.put(:fenced, false)
  end

  defp do_apply(state, %{type: "session.waiting", payload: payload}) do
    state
    |> Map.put(:phase, "waiting")
    |> Map.put(:wait_reason, payload.reason)
  end

  defp do_apply(state, %{type: "session.resumed"}) do
    state
    |> Map.put(:phase, "active")
    |> Map.put(:wait_reason, "none")
  end

  defp do_apply(state, %{type: "session.cancelling"}) do
    state
    |> Map.put(:phase, "cancelling")
    |> Map.put(:wait_reason, "none")
  end

  defp do_apply(state, %{type: "session.completed"}) do
    state
    |> Map.put(:phase, "terminal")
    |> Map.put(:wait_reason, "none")
  end

  defp do_apply(state, %{type: "session.failed"}) do
    state
    |> Map.put(:phase, "terminal")
    |> Map.put(:wait_reason, "none")
    |> Map.put(:health, "degraded")
  end

  defp do_apply(state, %{type: "session.quarantined", payload: payload}) do
    state
    |> Map.put(:health, "quarantined")
    |> Map.put(:latest_recovery_reason, payload.reason)
  end

  defp do_apply(state, %{type: "system.lease_lost", payload: payload}) do
    state
    |> Map.put(:owner_node, payload.owner_node)
    |> Map.put(:lease_epoch, payload.lease_epoch)
    |> Map.put(:fenced, true)
  end

  defp do_apply(state, %{type: "system.node_recovered", payload: payload}) do
    state
    |> Map.put(:owner_node, payload.owner_node)
    |> Map.put(:lease_epoch, payload.lease_epoch)
    |> Map.put(:health, "healthy")
    |> Map.put(:latest_recovery_reason, payload.recovery_reason)
    |> Map.put(:fenced, false)
  end

  defp do_apply(state, %{type: "system.worker_lost", payload: payload}) do
    state
    |> Map.put(:health, "degraded")
    |> Map.put(:latest_recovery_reason, payload.reason)
    |> Map.put(
      :action_ledger,
      update_action_by_execution(state.action_ledger, payload.execution_id, fn action ->
        action
        |> Map.put(:status, "uncertain")
        |> Map.put(:uncertain_side_effect, true)
      end)
    )
  end

  defp do_apply(state, %{type: "health.degraded", payload: payload}) do
    state
    |> Map.put(:health, "degraded")
    |> Map.put(:latest_recovery_reason, payload.health_reason)
  end

  defp do_apply(state, %{type: "session.mode_changed", payload: payload}) do
    Map.put(state, :control_mode, payload.control_mode)
  end

  defp do_apply(state, %{type: "action.requested", payload: payload}) do
    tool_id = payload.tool_id

    action = %{
      action_id: payload.action_id,
      tool_id: tool_id,
      tool_schema_version: Map.get(payload, :tool_schema_version, "v1"),
      worker_kind: Map.get(payload, :worker_kind, derive_worker_kind(tool_id)),
      input: Map.get(payload, :input, %{}),
      status: "requested",
      risk_class: Map.get(payload, :risk_class, "read_only"),
      idempotency_class: Map.get(payload, :idempotency_class, "unknown"),
      idempotency_key: Map.get(payload, :idempotency_key),
      timeout_class: Map.get(payload, :timeout_class, "standard"),
      mutating: Map.get(payload, :mutating, false),
      execution_id: nil,
      uncertain_side_effect: false,
      accept_deadline: Map.get(payload, :accept_deadline),
      soft_deadline: Map.get(payload, :soft_deadline),
      hard_deadline: Map.get(payload, :hard_deadline),
      capability_token_ref: Map.get(payload, :capability_token_ref),
      approved_argument_digest: Map.get(payload, :approved_argument_digest),
      trace_id: Map.get(payload, :trace_id)
    }

    Map.put(state, :action_ledger, upsert(state.action_ledger, action, :action_id))
  end

  defp do_apply(state, %{type: "action.dispatched", payload: payload}) do
    Map.put(
      state,
      :action_ledger,
      update_action(state.action_ledger, payload.action_id, fn action ->
        action
        |> Map.put(:status, "dispatched")
        |> Map.put(:execution_id, payload.execution_id)
        |> Map.put(:worker_kind, payload.worker_kind)
        |> Map.put(:accept_deadline, payload.accept_deadline)
      end)
    )
  end

  defp do_apply(state, %{type: "action.progressed", payload: payload}) do
    Map.put(
      state,
      :action_ledger,
      update_action(state.action_ledger, payload.action_id, fn action ->
        action
        |> Map.put(:status, "in_progress")
        |> Map.put(:execution_id, payload.execution_id)
      end)
    )
  end

  defp do_apply(state, %{type: "action.heartbeat_missed", payload: payload}) do
    Map.put(
      state,
      :action_ledger,
      update_action_by_execution(state.action_ledger, payload.execution_id, fn action ->
        action
        |> Map.put(:status, "uncertain")
        |> Map.put(:uncertain_side_effect, true)
      end)
    )
  end

  defp do_apply(state, %{type: "action.succeeded", payload: payload}) do
    Map.put(
      state,
      :action_ledger,
      update_action(state.action_ledger, payload.action_id, fn action ->
        action
        |> Map.put(:status, "succeeded")
        |> Map.put(:execution_id, payload.execution_id)
        |> Map.put(:uncertain_side_effect, false)
      end)
    )
  end

  defp do_apply(state, %{type: "action.failed", payload: payload}) do
    next_status =
      if Map.get(payload, :uncertain_side_effect, false), do: "uncertain", else: "failed"

    state
    |> Map.put(
      :action_ledger,
      update_action(state.action_ledger, payload.action_id, fn action ->
        action
        |> Map.put(:status, next_status)
        |> Map.put(:execution_id, payload.execution_id)
        |> Map.put(:uncertain_side_effect, Map.get(payload, :uncertain_side_effect, false))
      end)
    )
    |> maybe_degrade_health(Map.get(payload, :uncertain_side_effect, false))
  end

  defp do_apply(state, %{type: "action.cancel_requested", payload: payload}) do
    Map.put(
      state,
      :action_ledger,
      update_action(state.action_ledger, payload.action_id, fn action ->
        action
        |> Map.put(:status, "cancellation_requested")
        |> Map.put(:execution_id, payload.execution_id)
      end)
    )
  end

  defp do_apply(state, %{type: "action.cancelled", payload: payload}) do
    Map.put(
      state,
      :action_ledger,
      update_action(state.action_ledger, payload.action_id, fn action ->
        action
        |> Map.put(:status, "cancelled")
        |> Map.put(:execution_id, payload.execution_id)
        |> Map.put(:uncertain_side_effect, false)
      end)
    )
  end

  defp do_apply(state, %{type: "approval.requested", payload: payload}) do
    approval = %{
      approval_id: payload.approval_id,
      action_id: payload.action_id,
      action_hash: payload.action_hash,
      status: "pending",
      risk_class: payload.risk_class,
      expires_at: payload.expires_at,
      decided_by: nil
    }

    Map.put(state, :pending_approvals, upsert(state.pending_approvals, approval, :approval_id))
  end

  defp do_apply(state, %{type: "artifact.registered", payload: payload}) do
    artifact = %{
      artifact_id: payload.artifact_id,
      artifact_kind: payload.artifact_kind,
      sha256: payload.sha256,
      content_type: payload.content_type,
      size_bytes: payload.size_bytes,
      retention_class: payload.retention_class,
      redaction_state: payload.redaction_state
    }

    state
    |> Map.put(:artifact_ids, Enum.uniq(state.artifact_ids ++ [payload.artifact_id]))
    |> Map.put(:recent_artifacts, upsert(state.recent_artifacts, artifact, :artifact_id))
  end

  defp do_apply(state, %{type: "agent.spawned", payload: payload}) do
    agent = %{
      agent_id: Map.get(payload, :agent_id, "unknown-agent"),
      role: Map.get(payload, :role, "assistant"),
      goal: Map.get(payload, :goal, ""),
      tool_allowlist: Map.get(payload, :tool_allowlist, []),
      budget: Map.get(payload, :budget),
      state_summary: Map.get(payload, :state_summary)
    }

    Map.put(state, :child_agents, upsert(state.child_agents, agent, :agent_id))
  end

  defp do_apply(state, %{type: "checkpoint.created", payload: payload}) do
    Map.put(state, :latest_checkpoint_id, payload.checkpoint_id)
  end

  defp do_apply(state, %{type: "checkpoint.restored", payload: payload}) do
    state
    |> Map.put(:latest_checkpoint_id, payload.checkpoint_id)
    |> Map.put(:last_seq_no, payload.restored_seq_no)
  end

  defp do_apply(state, _envelope), do: state

  defp update_action(actions, action_id, fun) do
    actions
    |> Enum.map(fn action ->
      if action.action_id == action_id, do: fun.(action), else: action
    end)
    |> Enum.sort_by(& &1.action_id)
  end

  defp update_action_by_execution(actions, execution_id, fun) do
    actions
    |> Enum.map(fn action ->
      if Map.get(action, :execution_id) == execution_id, do: fun.(action), else: action
    end)
    |> Enum.sort_by(& &1.action_id)
  end

  defp maybe_degrade_health(state, true), do: Map.put(state, :health, "degraded")
  defp maybe_degrade_health(state, false), do: state

  defp derive_worker_kind(tool_id) when is_binary(tool_id) do
    tool_id
    |> String.split(".", parts: 2)
    |> List.first()
  end

  defp derive_worker_kind(_tool_id), do: "tool"

  defp upsert(entries, entry, key) do
    entries
    |> Enum.reject(&(Map.fetch!(&1, key) == Map.fetch!(entry, key)))
    |> Kernel.++([entry])
    |> Enum.sort_by(&Map.fetch!(&1, key))
  end
end
