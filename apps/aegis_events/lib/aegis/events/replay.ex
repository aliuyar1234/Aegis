defmodule Aegis.Events.Replay do
  @moduledoc false

  def initial_state(session_row) do
    %{
      tenant_id: session_row.tenant_id,
      workspace_id: session_row.workspace_id,
      isolation_tier: Map.get(session_row, :isolation_tier, "tier_a"),
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
      isolation_tier: Map.get(payload, :isolation_tier, Map.get(session_row, :isolation_tier, "tier_a")),
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
    |> Map.put(:isolation_tier, Map.get(payload, :isolation_tier, Map.get(state, :isolation_tier, "tier_a")))
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
    |> Map.put(:phase, "waiting")
    |> Map.put(:health, "quarantined")
    |> Map.put(:wait_reason, "external_dependency")
    |> Map.put(:fenced, true)
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
      isolation_tier: Map.get(payload, :isolation_tier, Map.get(state, :isolation_tier, "tier_a")),
      worker_pool_id: Map.get(payload, :worker_pool_id),
      dispatch_route_key: Map.get(payload, :dispatch_route_key),
      input: Map.get(payload, :input, %{}),
      status: "requested",
      risk_class: Map.get(payload, :risk_class, "read_only"),
      dangerous_action_class: Map.get(payload, :dangerous_action_class),
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
      action_hash: Map.get(payload, :action_hash),
      policy_decision: Map.get(payload, :policy_decision),
      policy_reason: Map.get(payload, :policy_reason),
      trace_id: Map.get(payload, :trace_id)
    }

    Map.put(state, :action_ledger, upsert(state.action_ledger, action, :action_id))
  end

  defp do_apply(state, %{type: "policy.evaluated", payload: payload}) do
    Map.put(
      state,
      :action_ledger,
      update_action(state.action_ledger, payload.action_id, fn action ->
        action
        |> Map.put(:action_hash, payload.action_hash)
        |> Map.put(:risk_class, payload.risk_class)
        |> Map.put(:dangerous_action_class, Map.get(payload, :dangerous_action_class))
        |> Map.put(:policy_decision, payload.decision)
        |> Map.put(:policy_reason, payload.reason)
        |> Map.put(:status, policy_status(payload.decision, action.status))
      end)
    )
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
        |> Map.put(:isolation_tier, Map.get(payload, :isolation_tier, Map.get(action, :isolation_tier)))
        |> Map.put(:worker_pool_id, Map.get(payload, :worker_pool_id, Map.get(action, :worker_pool_id)))
        |> Map.put(:dispatch_route_key, Map.get(payload, :dispatch_route_key, Map.get(action, :dispatch_route_key)))
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
    |> maybe_degrade_health(
      Map.get(payload, :uncertain_side_effect, false) or browser_instability_failure?(payload),
      payload
    )
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

  defp do_apply(state, %{type: "operator.joined"}) do
    state
  end

  defp do_apply(state, %{type: "operator.note_added", payload: payload}) do
    note = %{
      note_ref: payload.note_ref,
      operator_id: payload.operator_id,
      note_text: Map.get(payload, :note_text, ""),
      recorded_at: Map.get(payload, :recorded_at)
    }

    summary_capsule =
      state.summary_capsule
      |> Map.put_new(:operator_notes, [])
      |> Map.update!(:operator_notes, fn notes ->
        (notes ++ [note])
        |> Enum.sort_by(& &1.note_ref)
      end)

    Map.put(state, :summary_capsule, summary_capsule)
  end

  defp do_apply(state, %{type: "operator.paused"}) do
    state
    |> Map.put(:phase, "waiting")
    |> Map.put(:control_mode, "paused")
    |> Map.put(:wait_reason, "operator")
  end

  defp do_apply(state, %{type: "operator.abort_requested"}) do
    state
    |> Map.put(:phase, "cancelling")
    |> Map.put(:wait_reason, "none")
  end

  defp do_apply(state, %{type: "operator.took_control"}) do
    state
    |> Map.put(:phase, "waiting")
    |> Map.put(:control_mode, "human_control")
    |> Map.put(:wait_reason, "operator")
  end

  defp do_apply(state, %{type: "operator.returned_control", payload: payload}) do
    state
    |> Map.put(:phase, "active")
    |> Map.put(:wait_reason, "none")
    |> Map.put(:latest_recovery_reason, payload.return_context)
  end

  defp do_apply(state, %{type: "approval.requested", payload: payload}) do
    approval = %{
      approval_id: payload.approval_id,
      action_id: payload.action_id,
      action_hash: payload.action_hash,
      status: "pending",
      risk_class: payload.risk_class,
      dangerous_action_class: Map.get(payload, :dangerous_action_class),
      expires_at: payload.expires_at,
      decided_by: nil,
      evidence_artifact_ids: Map.get(payload, :evidence_artifact_ids, []),
      requested_by: Map.get(payload, :requested_by),
      tool_id: Map.get(payload, :tool_id)
    }

    Map.put(state, :pending_approvals, upsert(state.pending_approvals, approval, :approval_id))
  end

  defp do_apply(state, %{type: "approval.granted", payload: payload}) do
    state
    |> Map.put(:pending_approvals, remove_approval(state.pending_approvals, payload.approval_id))
    |> Map.put(
      :action_ledger,
      update_action(state.action_ledger, payload.action_id, fn action ->
        action
        |> Map.put(:status, "requested")
        |> Map.put(:approved_argument_digest, Map.get(payload, :approved_argument_digest))
        |> Map.put(:capability_token_ref, Map.get(payload, :capability_token_ref))
      end)
    )
  end

  defp do_apply(state, %{type: "approval.denied", payload: payload}) do
    state
    |> Map.put(:pending_approvals, remove_approval(state.pending_approvals, payload.approval_id))
    |> Map.put(
      :action_ledger,
      update_action(state.action_ledger, payload.action_id, fn action ->
        action
        |> Map.put(:status, "denied")
        |> Map.put(:policy_reason, Map.get(payload, :reason))
      end)
    )
  end

  defp do_apply(state, %{type: "approval.expired", payload: payload}) do
    state
    |> Map.put(:pending_approvals, remove_approval(state.pending_approvals, payload.approval_id))
    |> Map.put(
      :action_ledger,
      update_action(state.action_ledger, payload.action_id, fn action ->
        action
        |> Map.put(:status, "approval_expired")
        |> Map.put(:policy_reason, "approval_expired")
      end)
    )
  end

  defp do_apply(state, %{type: "artifact.registered", payload: payload}) do
    artifact = %{
      artifact_id: payload.artifact_id,
      artifact_kind: payload.artifact_kind,
      sha256: payload.sha256,
      content_type: payload.content_type,
      size_bytes: payload.size_bytes,
      retention_class: payload.retention_class,
      redaction_state: payload.redaction_state,
      storage_ref: Map.get(payload, :storage_ref),
      recorded_at: Map.get(payload, :recorded_at),
      action_id: Map.get(payload, :action_id)
    }

    state
    |> Map.put(:artifact_ids, Enum.uniq(state.artifact_ids ++ [payload.artifact_id]))
    |> Map.put(:recent_artifacts, upsert(state.recent_artifacts, artifact, :artifact_id))
    |> maybe_update_browser_handle_from_artifact(payload)
  end

  defp do_apply(state, %{type: "observation.browser_snapshot_added", payload: payload}) do
    Map.put(
      state,
      :browser_handles,
      update_browser_handle(state.browser_handles, payload.browser_handle_id, fn handle ->
        handle
        |> Map.put(:state_ref, payload.browser_snapshot_ref)
        |> Map.put(:last_stable_artifact_id, payload.artifact_id)
        |> Map.put(:last_observed_at, Map.get(handle, :last_observed_at))
      end)
    )
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

  defp remove_approval(approvals, approval_id) do
    approvals
    |> Enum.reject(&(&1.approval_id == approval_id))
    |> Enum.sort_by(& &1.approval_id)
  end

  defp policy_status("require_approval", _current_status), do: "awaiting_approval"
  defp policy_status("deny", _current_status), do: "denied"
  defp policy_status(_decision, current_status), do: current_status

  defp maybe_degrade_health(state, true, payload) do
    recovery_reason =
      cond do
        browser_instability_failure?(payload) -> "browser_instability:" <> to_string(Map.get(payload, :error_class))
        true -> Map.get(state, :latest_recovery_reason)
      end

    state
    |> Map.put(:health, "degraded")
    |> maybe_mark_browser_recovery(browser_instability_failure?(payload), recovery_reason)
  end

  defp maybe_degrade_health(state, false, _payload), do: state

  defp maybe_mark_browser_recovery(state, true, recovery_reason) do
    state
    |> Map.put(:phase, "waiting")
    |> Map.put(:wait_reason, "external_dependency")
    |> Map.put(:latest_recovery_reason, recovery_reason)
  end

  defp maybe_mark_browser_recovery(state, false, _recovery_reason), do: state

  defp maybe_update_browser_handle_from_artifact(state, payload) do
    browser_handle_id = Map.get(payload, :browser_handle_id)

    if is_binary(browser_handle_id) do
      Map.put(
        state,
        :browser_handles,
        update_browser_handle(state.browser_handles, browser_handle_id, fn handle ->
          handle
          |> Map.put(:browser_handle_id, browser_handle_id)
          |> Map.put(:provider_kind, Map.get(payload, :provider_kind, Map.get(handle, :provider_kind, "playwright")))
          |> Map.put(:page_ref, Map.get(payload, :page_ref, Map.get(handle, :page_ref)))
          |> Map.put(:current_url, Map.get(payload, :current_url, Map.get(handle, :current_url)))
          |> Map.put(:state_ref, Map.get(payload, :browser_snapshot_ref, Map.get(handle, :state_ref)))
          |> Map.put(:last_stable_artifact_id, payload.artifact_id)
          |> Map.put(:last_observed_at, Map.get(payload, :recorded_at))
          |> Map.put(:restart_hint, Map.get(payload, :restart_hint, Map.get(handle, :restart_hint)))
          |> Map.put(:provider_session_ref, Map.get(payload, :provider_session_ref, Map.get(handle, :provider_session_ref)))
          |> Map.put(:read_only_baseline_complete, Map.get(payload, :read_only_baseline_complete, Map.get(handle, :read_only_baseline_complete, false)))
        end)
      )
    else
      state
    end
  end

  defp update_browser_handle(handles, browser_handle_id, fun) do
    current =
      Enum.find(handles, &(Map.get(&1, :browser_handle_id) == browser_handle_id)) ||
        %{browser_handle_id: browser_handle_id, recovery_attempts: 0}

    upsert(handles, fun.(current), :browser_handle_id)
  end

  defp browser_instability_failure?(payload) do
    Map.get(payload, :error_class) in ["browser_instability", "browser_disconnect", "page_crash", "dom_drift", "navigation_timeout"] or
      Map.get(payload, :error_code) in ["page_crash", "browser_disconnect", "dom_drift", "navigation_timeout"]
  end

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
