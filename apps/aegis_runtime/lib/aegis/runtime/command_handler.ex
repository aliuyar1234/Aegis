defmodule Aegis.Runtime.CommandHandler do
  @moduledoc """
  Pure command handler for the SessionKernel.

  Commands update authoritative session state, emit deterministic runtime events,
  and refresh the stable operator projection without touching transport or store
  internals directly.
  """

  alias Aegis.Runtime.{Event, SessionState}

  @type command ::
          {:hydrate, map()}
          | {:activate, map()}
          | {:adopt, map()}
          | {:report_lease_ambiguity, map()}
          | {:wait, SessionState.wait_reason(), map()}
          | {:resume, map()}
          | {:cancel, map()}
          | {:complete, map()}
          | {:fail, map()}
          | {:change_control_mode, SessionState.control_mode(), map()}
          | {:request_action, map()}
          | {:dispatch_action, map()}
          | {:record_action_progress, map()}
          | {:record_action_succeeded, map()}
          | {:record_action_failed, map()}
          | {:request_action_cancel, map()}
          | {:record_action_cancelled, map()}
          | {:record_worker_lost, map()}
          | {:request_approval, map()}
          | {:register_artifact, map()}
          | {:spawn_agent, map()}
          | {:quarantine, map()}

  @wait_reasons [:action, :approval, :timer, :external_dependency, :operator, :lease_recovery]
  @terminal_action_statuses ["succeeded", "failed", "cancelled", "uncertain"]

  @spec bootstrap(SessionState.t(), map()) :: {:ok, SessionState.t(), [Event.t()]}
  def bootstrap(state, metadata \\ %{})

  def bootstrap(%SessionState{} = state, metadata) do
    payload = %{
      session_kind: state.durable.session_kind,
      requested_by: state.durable.requested_by
    }

    emit(state, "session.created", payload, %{}, metadata)
  end

  @spec handle(SessionState.t(), command(), map()) ::
          {:ok, SessionState.t(), [Event.t()]} | {:error, term()}
  def handle(state, command, metadata \\ %{})

  def handle(%SessionState{} = state, {:hydrate, attrs}, metadata) do
    ensure_phase!(state, [:provisioning])

    restored_from_checkpoint_id = Map.fetch!(attrs, :restored_from_checkpoint_id)

    emit(
      state,
      "session.hydrated",
      %{
        owner_node: state.durable.owner_node,
        lease_epoch: state.durable.lease_epoch,
        restored_from_checkpoint_id: restored_from_checkpoint_id
      },
      %{
        phase: :hydrating,
        wait_reason: :none,
        latest_checkpoint_id: restored_from_checkpoint_id,
        latest_recovery_reason:
          Map.get(attrs, :recovery_reason, state.durable.latest_recovery_reason)
      },
      metadata
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:activate, attrs}, metadata) do
    ensure_phase!(state, [:provisioning, :hydrating, :waiting])

    emit(
      state,
      "session.owned",
      %{
        owner_node: state.durable.owner_node,
        lease_epoch: max(state.durable.lease_epoch, 1),
        adoption_reason: Map.get(attrs, :adoption_reason, "phase_01_activation")
      },
      %{
        phase: :active,
        wait_reason: :none,
        fenced: false,
        health: :healthy
      },
      metadata
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:adopt, attrs}, metadata) do
    ensure_phase!(state, [:provisioning, :hydrating, :active, :waiting])

    restored_from_checkpoint_id =
      Map.get(attrs, :restored_from_checkpoint_id, state.durable.latest_checkpoint_id)

    recovery_reason = Map.get(attrs, :recovery_reason, "lease_recovery")

    emit_many(
      state,
      [
        {"session.hydrated",
         %{
           owner_node: state.durable.owner_node,
           lease_epoch: state.durable.lease_epoch,
           restored_from_checkpoint_id: restored_from_checkpoint_id
         }},
        {"session.owned",
         %{
           owner_node: state.durable.owner_node,
           lease_epoch: state.durable.lease_epoch,
           adoption_reason: recovery_reason
         }},
        {"system.node_recovered",
         %{
           owner_node: state.durable.owner_node,
           lease_epoch: state.durable.lease_epoch,
           recovery_reason: recovery_reason
         }}
      ],
      %{
        phase: :active,
        wait_reason: :none,
        health: :healthy,
        latest_checkpoint_id: restored_from_checkpoint_id,
        latest_recovery_reason: recovery_reason,
        fenced: false
      },
      metadata
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:report_lease_ambiguity, attrs}, metadata) do
    ensure_phase!(state, [:provisioning, :hydrating, :active, :waiting, :cancelling])

    reason = Map.get(attrs, :reason, "lease_ambiguity")

    emit_many(
      state,
      [
        {"system.lease_lost",
         %{
           owner_node: state.durable.owner_node,
           lease_epoch: state.durable.lease_epoch
         }},
        {"health.degraded",
         %{
           health_scope: "session",
           health_reason: reason
         }},
        {"session.waiting",
         %{
           reason: "lease_recovery",
           detail: reason,
           blocking_action_id: Map.get(attrs, :blocking_action_id),
           blocking_approval_id: Map.get(attrs, :blocking_approval_id)
         }}
      ],
      %{
        phase: :waiting,
        wait_reason: :lease_recovery,
        health: :degraded,
        latest_recovery_reason: reason,
        fenced: true
      },
      metadata
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:wait, reason, attrs}, metadata) do
    ensure_phase!(state, [:active])

    if reason not in @wait_reasons do
      {:error, {:invalid_wait_reason, reason}}
    else
      emit(
        state,
        "session.waiting",
        %{
          reason: to_string(reason),
          detail: Map.get(attrs, :detail),
          blocking_action_id: Map.get(attrs, :blocking_action_id),
          blocking_approval_id: Map.get(attrs, :blocking_approval_id)
        },
        %{
          phase: :waiting,
          wait_reason: reason
        },
        metadata
      )
    end
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:resume, attrs}, metadata) do
    ensure_phase!(state, [:waiting])

    emit(
      state,
      "session.resumed",
      %{
        reason: Map.get(attrs, :reason, "resume")
      },
      %{
        phase: :active,
        wait_reason: :none
      },
      metadata
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:cancel, attrs}, metadata) do
    ensure_phase!(state, [:provisioning, :hydrating, :active, :waiting])

    emit(
      state,
      "session.cancelling",
      %{
        reason: Map.get(attrs, :reason, "cancel_requested")
      },
      %{
        phase: :cancelling,
        wait_reason: :none
      },
      metadata
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:complete, attrs}, metadata) do
    ensure_phase!(state, [:active, :waiting, :cancelling])

    emit(
      state,
      "session.completed",
      %{
        reason: Map.get(attrs, :reason, "completed")
      },
      %{
        phase: :terminal,
        wait_reason: :none
      },
      metadata
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:fail, attrs}, metadata) do
    ensure_phase!(state, [:active, :waiting, :cancelling, :hydrating])

    emit(
      state,
      "session.failed",
      %{
        reason: Map.get(attrs, :reason, "failed")
      },
      %{
        phase: :terminal,
        wait_reason: :none,
        health: :degraded
      },
      metadata
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:change_control_mode, control_mode, attrs}, metadata) do
    emit(
      state,
      "session.mode_changed",
      %{
        control_mode: to_string(control_mode),
        reason: Map.get(attrs, :reason, "mode_change")
      },
      %{
        control_mode: control_mode
      },
      metadata
    )
  end

  def handle(%SessionState{} = state, {:request_action, attrs}, metadata) do
    ensure_phase!(state, [:active, :waiting])

    normalized_meta = event_meta(metadata, attrs)

    action = %{
      action_id: Map.fetch!(attrs, :action_id),
      tool_id: Map.fetch!(attrs, :tool_id),
      tool_schema_version: Map.get(attrs, :tool_schema_version, "v1"),
      worker_kind: Map.get(attrs, :worker_kind, derive_worker_kind(Map.fetch!(attrs, :tool_id))),
      input: Map.get(attrs, :input, %{}),
      status: "requested",
      risk_class: Map.get(attrs, :risk_class, "read_only"),
      idempotency_class: Map.get(attrs, :idempotency_class, "unknown"),
      idempotency_key:
        Map.get(attrs, :idempotency_key, Map.get(normalized_meta, :idempotency_key)),
      timeout_class: Map.get(attrs, :timeout_class, "standard"),
      mutating: Map.get(attrs, :mutating, false),
      execution_id: nil,
      uncertain_side_effect: false,
      accept_deadline: Map.get(attrs, :accept_deadline),
      soft_deadline: Map.get(attrs, :soft_deadline),
      hard_deadline: Map.get(attrs, :hard_deadline),
      capability_token_ref: Map.get(attrs, :capability_token_ref),
      approved_argument_digest: Map.get(attrs, :approved_argument_digest),
      trace_id: Map.get(attrs, :trace_id, Map.get(normalized_meta, :trace_id))
    }

    emit(
      state,
      "action.requested",
      %{
        action_id: action.action_id,
        tool_id: action.tool_id,
        tool_schema_version: action.tool_schema_version,
        worker_kind: action.worker_kind,
        input: action.input,
        risk_class: action.risk_class,
        idempotency_class: action.idempotency_class,
        idempotency_key: action.idempotency_key,
        timeout_class: action.timeout_class,
        mutating: action.mutating,
        accept_deadline: action.accept_deadline,
        soft_deadline: action.soft_deadline,
        hard_deadline: action.hard_deadline,
        trace_id: action.trace_id,
        capability_token_ref: action.capability_token_ref,
        approved_argument_digest: action.approved_argument_digest
      },
      %{
        action_ledger: upsert(state.durable.action_ledger, action, :action_id)
      },
      normalized_meta
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:dispatch_action, attrs}, metadata) do
    ensure_phase!(state, [:active, :waiting])

    action_id = Map.fetch!(attrs, :action_id)
    action = fetch_action!(state, action_id)

    if action.status in @terminal_action_statuses do
      {:error, {:action_already_terminal, action_id, action.status}}
    else
      updated_action =
        action
        |> Map.put(:status, "dispatched")
        |> Map.put(:execution_id, Map.fetch!(attrs, :execution_id))
        |> Map.put(:worker_kind, Map.fetch!(attrs, :worker_kind))
        |> Map.put(:accept_deadline, Map.fetch!(attrs, :accept_deadline))
        |> Map.put(:soft_deadline, Map.get(attrs, :soft_deadline, action.soft_deadline))
        |> Map.put(:hard_deadline, Map.get(attrs, :hard_deadline, action.hard_deadline))

      emit(
        state,
        "action.dispatched",
        %{
          action_id: updated_action.action_id,
          execution_id: updated_action.execution_id,
          worker_kind: updated_action.worker_kind,
          worker_subject: Map.fetch!(attrs, :worker_subject),
          accept_deadline: updated_action.accept_deadline,
          contract_version: Map.get(attrs, :contract_version, "v1"),
          capability_token_required: Map.get(attrs, :capability_token_required, false),
          trace_id: Map.get(attrs, :trace_id, updated_action.trace_id),
          idempotency_key: Map.get(attrs, :idempotency_key, updated_action.idempotency_key)
        },
        %{action_ledger: replace_action(state.durable.action_ledger, updated_action)},
        event_meta(metadata, attrs)
      )
    end
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:record_action_progress, attrs}, metadata) do
    ensure_phase!(state, [:active, :waiting])

    action = fetch_action!(state, Map.fetch!(attrs, :action_id))

    updated_action =
      action
      |> Map.put(:status, "in_progress")
      |> Map.put(:execution_id, Map.fetch!(attrs, :execution_id))

    emit(
      state,
      "action.progressed",
      %{
        action_id: updated_action.action_id,
        execution_id: updated_action.execution_id,
        progress_kind: Map.fetch!(attrs, :progress_kind),
        progress_seq: Map.fetch!(attrs, :progress_seq),
        observed_at: Map.fetch!(attrs, :observed_at),
        worker_id: Map.get(attrs, :worker_id),
        progress: Map.get(attrs, :progress, %{}),
        artifact_refs: Map.get(attrs, :artifact_refs, [])
      },
      %{action_ledger: replace_action(state.durable.action_ledger, updated_action)},
      event_meta(metadata, attrs)
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:record_action_succeeded, attrs}, metadata) do
    ensure_phase!(state, [:active, :waiting])

    action = fetch_action!(state, Map.fetch!(attrs, :action_id))

    updated_action =
      action
      |> Map.put(:status, "succeeded")
      |> Map.put(:execution_id, Map.fetch!(attrs, :execution_id))
      |> Map.put(:uncertain_side_effect, false)

    emit(
      state,
      "action.succeeded",
      %{
        action_id: updated_action.action_id,
        execution_id: updated_action.execution_id,
        completed_at: Map.fetch!(attrs, :completed_at),
        normalized_result: Map.fetch!(attrs, :normalized_result),
        raw_result_artifact_id: Map.fetch!(attrs, :raw_result_artifact_id)
      },
      %{action_ledger: replace_action(state.durable.action_ledger, updated_action)},
      event_meta(metadata, attrs)
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:record_action_failed, attrs}, metadata) do
    ensure_phase!(state, [:active, :waiting])

    action = fetch_action!(state, Map.fetch!(attrs, :action_id))
    uncertain_side_effect = Map.get(attrs, :uncertain_side_effect, false)
    next_status = if uncertain_side_effect, do: "uncertain", else: "failed"

    updated_action =
      action
      |> Map.put(:status, next_status)
      |> Map.put(:execution_id, Map.fetch!(attrs, :execution_id))
      |> Map.put(:uncertain_side_effect, uncertain_side_effect)

    durable_changes =
      %{
        action_ledger: replace_action(state.durable.action_ledger, updated_action)
      }
      |> maybe_merge_health(uncertain_side_effect)

    emit(
      state,
      "action.failed",
      %{
        action_id: updated_action.action_id,
        execution_id: updated_action.execution_id,
        error_class: Map.fetch!(attrs, :error_class),
        error_code: Map.fetch!(attrs, :error_code),
        retryable: Map.get(attrs, :retryable),
        safe_to_retry: Map.get(attrs, :safe_to_retry),
        compensation_possible: Map.get(attrs, :compensation_possible),
        uncertain_side_effect: uncertain_side_effect,
        details_artifact_id: Map.get(attrs, :details_artifact_id),
        failed_at: Map.fetch!(attrs, :failed_at)
      },
      durable_changes,
      event_meta(metadata, attrs)
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:request_action_cancel, attrs}, metadata) do
    ensure_phase!(state, [:active, :waiting, :cancelling])

    action = fetch_action!(state, Map.fetch!(attrs, :action_id))

    updated_action =
      action
      |> Map.put(:status, "cancellation_requested")
      |> Map.put(:execution_id, Map.fetch!(attrs, :execution_id))

    cancel_requested_at =
      Map.get(
        attrs,
        :cancel_requested_at,
        DateTime.utc_now() |> DateTime.truncate(:second) |> DateTime.to_iso8601()
      )

    emit(
      state,
      "action.cancel_requested",
      %{
        action_id: updated_action.action_id,
        execution_id: updated_action.execution_id,
        reason: Map.fetch!(attrs, :reason),
        cancel_requested_at: cancel_requested_at
      },
      %{action_ledger: replace_action(state.durable.action_ledger, updated_action)},
      event_meta(metadata, attrs)
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:record_action_cancelled, attrs}, metadata) do
    ensure_phase!(state, [:active, :waiting, :cancelling])

    action = fetch_action!(state, Map.fetch!(attrs, :action_id))

    updated_action =
      action
      |> Map.put(:status, "cancelled")
      |> Map.put(:execution_id, Map.fetch!(attrs, :execution_id))
      |> Map.put(:uncertain_side_effect, false)

    emit(
      state,
      "action.cancelled",
      %{
        action_id: updated_action.action_id,
        execution_id: updated_action.execution_id,
        worker_id: Map.fetch!(attrs, :worker_id),
        reason: Map.get(attrs, :reason),
        cancelled_at: Map.fetch!(attrs, :cancelled_at)
      },
      %{action_ledger: replace_action(state.durable.action_ledger, updated_action)},
      event_meta(metadata, attrs)
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:record_worker_lost, attrs}, metadata) do
    ensure_phase!(state, [:active, :waiting, :cancelling])

    action = fetch_action!(state, Map.fetch!(attrs, :action_id))

    updated_action =
      action
      |> Map.put(:status, "uncertain")
      |> Map.put(:execution_id, Map.fetch!(attrs, :execution_id))
      |> Map.put(:uncertain_side_effect, true)

    emit_many(
      state,
      [
        {"action.heartbeat_missed",
         %{
           action_id: updated_action.action_id,
           execution_id: updated_action.execution_id
         }},
        {"system.worker_lost",
         %{
           action_id: updated_action.action_id,
           execution_id: updated_action.execution_id,
           worker_id: Map.fetch!(attrs, :worker_id),
           reason: Map.fetch!(attrs, :reason),
           last_heartbeat_at: Map.get(attrs, :last_heartbeat_at)
         }},
        {"health.degraded",
         %{
           health_scope: "session",
           health_reason: "worker_lost"
         }}
      ],
      %{
        action_ledger: replace_action(state.durable.action_ledger, updated_action),
        health: :degraded
      },
      event_meta(metadata, attrs)
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:request_approval, attrs}, metadata) do
    approval = %{
      approval_id: Map.fetch!(attrs, :approval_id),
      action_id: Map.fetch!(attrs, :action_id),
      action_hash: Map.fetch!(attrs, :action_hash),
      status: Map.get(attrs, :status, "pending"),
      risk_class: Map.get(attrs, :risk_class, "high"),
      expires_at: Map.fetch!(attrs, :expires_at),
      decided_by: Map.get(attrs, :decided_by)
    }

    emit(
      state,
      "approval.requested",
      %{
        approval_id: approval.approval_id,
        action_id: approval.action_id,
        action_hash: approval.action_hash,
        expires_at: approval.expires_at,
        risk_class: approval.risk_class,
        lease_epoch: state.durable.lease_epoch
      },
      %{
        pending_approvals: upsert(state.durable.pending_approvals, approval, :approval_id)
      },
      event_meta(metadata, attrs)
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:register_artifact, attrs}, metadata) do
    artifact = %{
      artifact_id: Map.fetch!(attrs, :artifact_id),
      artifact_kind: Map.fetch!(attrs, :artifact_kind),
      storage_ref: Map.get(attrs, :storage_ref),
      recorded_at:
        Map.get(
          attrs,
          :recorded_at,
          DateTime.utc_now() |> DateTime.truncate(:second) |> DateTime.to_iso8601()
        )
    }

    emit(
      state,
      "artifact.registered",
      %{
        artifact_id: artifact.artifact_id,
        artifact_kind: artifact.artifact_kind,
        sha256: Map.get(attrs, :sha256, "sha256-unset"),
        content_type: Map.get(attrs, :content_type, "application/octet-stream"),
        size_bytes: Map.get(attrs, :size_bytes, 0),
        retention_class: Map.get(attrs, :retention_class, "standard"),
        redaction_state: Map.get(attrs, :redaction_state, "not_requested"),
        storage_ref: artifact.storage_ref,
        recorded_at: artifact.recorded_at,
        action_id: Map.get(attrs, :action_id)
      },
      %{
        artifact_ids: Enum.uniq(state.durable.artifact_ids ++ [artifact.artifact_id]),
        recent_artifacts: upsert(state.durable.recent_artifacts, artifact, :artifact_id)
      },
      event_meta(metadata, attrs)
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:spawn_agent, attrs}, metadata) do
    agent = %{
      agent_id: Map.fetch!(attrs, :agent_id),
      role: Map.fetch!(attrs, :role),
      goal: Map.fetch!(attrs, :goal),
      tool_allowlist: Map.get(attrs, :tool_allowlist, []),
      budget: Map.get(attrs, :budget),
      state_summary: Map.get(attrs, :state_summary)
    }

    emit(
      state,
      "agent.spawned",
      %{
        requested_by: Map.get(attrs, :requested_by, "session_kernel"),
        agent_id: agent.agent_id,
        role: agent.role,
        goal: agent.goal,
        tool_allowlist: agent.tool_allowlist,
        budget: agent.budget,
        state_summary: agent.state_summary
      },
      %{
        child_agents: upsert(state.durable.child_agents, agent, :agent_id)
      },
      event_meta(metadata, attrs)
    )
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  def handle(%SessionState{} = state, {:quarantine, attrs}, metadata) do
    emit(
      state,
      "session.quarantined",
      %{
        reason: Map.get(attrs, :reason, "quarantined")
      },
      %{
        health: :quarantined
      },
      metadata
    )
  end

  defp emit(state, type, payload, durable_changes, metadata) do
    state = SessionState.put_durable(state, durable_changes)

    event =
      Event.new(SessionState.next_seq_no(state), type, payload, normalize_metadata(metadata))

    next_state = SessionState.apply_event(state, event)
    {:ok, next_state, [event]}
  end

  defp emit_many(state, event_specs, durable_changes, metadata) do
    state = SessionState.put_durable(state, durable_changes)
    metadata = normalize_metadata(metadata)

    {events, next_state} =
      Enum.map_reduce(event_specs, state, fn {type, payload}, acc ->
        event = Event.new(SessionState.next_seq_no(acc), type, payload, metadata)
        {event, SessionState.apply_event(acc, event)}
      end)

    {:ok, next_state, events}
  end

  defp ensure_phase!(state, allowed_phases) do
    if state.durable.phase in allowed_phases do
      :ok
    else
      raise ArgumentError,
            "invalid phase transition from #{state.durable.phase} (allowed: #{Enum.join(Enum.map(allowed_phases, &to_string/1), ", ")})"
    end
  end

  defp fetch_action!(state, action_id) do
    Enum.find(state.durable.action_ledger, &(&1.action_id == action_id)) ||
      raise(ArgumentError, "unknown action #{inspect(action_id)}")
  end

  defp replace_action(actions, action) do
    upsert(actions, action, :action_id)
  end

  defp maybe_merge_health(changes, true), do: Map.put(changes, :health, :degraded)
  defp maybe_merge_health(changes, false), do: changes

  defp event_meta(metadata, attrs) do
    metadata
    |> Map.new()
    |> Map.merge(%{
      trace_id: Map.get(attrs, :trace_id, Map.get(metadata, :trace_id)),
      idempotency_key: Map.get(attrs, :idempotency_key, Map.get(metadata, :idempotency_key)),
      correlation_id: Map.get(attrs, :execution_id, Map.get(metadata, :correlation_id))
    })
  end

  defp normalize_metadata(metadata) do
    metadata
    |> Map.new()
    |> Map.take([
      :command_id,
      :correlation_id,
      :causation_id,
      :trace_id,
      :span_id,
      :idempotency_key
    ])
  end

  defp upsert(entries, entry, key) do
    entries
    |> Enum.reject(&(Map.fetch!(&1, key) == Map.fetch!(entry, key)))
    |> Kernel.++([entry])
    |> Enum.sort_by(&Map.fetch!(&1, key))
  end

  defp derive_worker_kind(tool_id) do
    tool_id
    |> String.split(".", parts: 2)
    |> List.first()
  end
end
