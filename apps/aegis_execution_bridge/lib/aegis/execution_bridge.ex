defmodule Aegis.ExecutionBridge do
  @moduledoc """
  Phase 04 execution bridge boundary.

  Source of truth:
  - phase doc: `docs/exec-plans/active/PHASE-04-worker-contracts-transport.md`
  - ADRs: `docs/adr/0007-nats-jetstream-transport.md`,
    `docs/adr/0008-protobuf-jsonschema-contracts.md`
  - acceptance: `AC-015`, `AC-016`, `AC-017`, `AC-018`, `AC-019`
  - tests: `TS-006`

  Owns:
  - dispatch from committed outbox intent into transport subjects
  - worker registration and worker/action heartbeat tracking
  - transport callback ingestion and timeout/loss handling
  - execution-attempt metadata that must stay off the canonical session tables

  Must not own:
  - canonical session truth (`aegis_runtime`)
  - canonical timeline and checkpoint persistence (`aegis_events`)
  - lease authority (`aegis_leases`)
  """

  alias Aegis.ExecutionBridge.{AdmissionControl, InMemoryTransport, Store, TransportTopology}
  alias Aegis.Runtime

  @dispatchable_event_types ["policy.evaluated", "approval.granted", "action.cancel_requested"]
  @terminal_statuses MapSet.new(["succeeded", "failed", "cancelled", "lost", "uncertain"])

  def flush_dispatches do
    @dispatchable_event_types
    |> Store.claim_outbox_rows()
    |> Enum.map(&flush_outbox_row/1)
  end

  def scan_timeouts(reference_time \\ DateTime.utc_now() |> DateTime.truncate(:second)) do
    heartbeat_policy = TransportTopology.heartbeat_expectation()

    Store.nonterminal_executions()
    |> Enum.map(&scan_execution(&1, reference_time, heartbeat_policy))
    |> Enum.reject(&is_nil/1)
  end

  def register_worker(attrs) do
    attrs = normalize_map(Map.new(attrs))

    with {:ok, _message} <-
           publish_transport(
             TransportTopology.subject_for(:worker_register, Map.fetch!(attrs, :worker_kind)),
             attrs,
             registry_headers()
           ) do
      {:ok, Store.fetch_worker_registration(Map.fetch!(attrs, :worker_id))}
    end
  end

  def worker_registrations do
    Store.worker_registrations()
  end

  def worker_heartbeat(attrs) do
    attrs = normalize_map(Map.new(attrs))

    case Store.fetch_worker_registration(Map.fetch!(attrs, :worker_id)) do
      nil ->
        {:error, :unknown_worker}

      registration ->
        with {:ok, _message} <-
               publish_transport(
                 TransportTopology.subject_for(:worker_heartbeat, registration.worker_kind),
                 attrs,
                 registry_headers()
               ) do
          {:ok, Store.fetch_worker_registration(registration.worker_id)}
        end
    end
  end

  def request_action_cancel(session_id, action_id, reason, opts \\ []) do
    case Store.fetch_execution_by_action(session_id, action_id) do
      nil ->
        {:error, :unknown_action_execution}

      execution ->
        with {:ok, session_ref} <- session_ref_for_session(session_id),
             {:ok, _result} <-
               dispatch_runtime_command(
                 session_ref,
                 {:request_action_cancel,
                  %{
                    action_id: action_id,
                    execution_id: execution.execution_id,
                    reason: reason
                  }},
                 Keyword.merge(
                   [
                     actor_kind: "system",
                     actor_id: "execution_bridge",
                     trace_id: execution.trace_id,
                     idempotency_key: execution.idempotency_key,
                     correlation_id: execution.execution_id
                   ],
                   opts
                 )
               ) do
          {:ok, execution.execution_id}
        end
    end
  end

  def accept_action(worker_kind, payload, headers \\ %{}),
    do: publish_worker_callback(:accepted, worker_kind, payload, headers)

  def progress_action(worker_kind, payload, headers \\ %{}),
    do: publish_worker_callback(:progress, worker_kind, payload, headers)

  def action_heartbeat(worker_kind, payload, headers \\ %{}),
    do: publish_worker_callback(:heartbeat, worker_kind, payload, headers)

  def complete_action(worker_kind, payload, headers \\ %{}),
    do: publish_worker_callback(:completed, worker_kind, payload, headers)

  def fail_action(worker_kind, payload, headers \\ %{}),
    do: publish_worker_callback(:failed, worker_kind, payload, headers)

  def cancel_action(worker_kind, payload, headers \\ %{}),
    do: publish_worker_callback(:cancelled, worker_kind, payload, headers)

  @doc false
  def process_worker_registration(attrs) do
    attrs = normalize_map(Map.new(attrs))
    contract_versions = Map.get(attrs, :supported_contract_versions, ["v1"])
    attributes =
      Map.get(attrs, :attributes, %{})
      |> Map.new()
      |> Map.put_new("worker_pool_id", Map.get(attrs, :worker_pool_id, "shared"))
      |> Map.put_new("isolation_tier", Map.get(attrs, :isolation_tier, "tier_a"))

    if "v1" in contract_versions do
      {:ok,
       Store.upsert_worker_registration(
         attrs
         |> Map.put(:supported_contract_versions, contract_versions)
         |> Map.put(:attributes, attributes)
         |> Map.put_new(:available_capacity, Map.get(attrs, :advertised_capacity, 0))
       )}
    else
      {:error, {:unsupported_contract_versions, contract_versions}}
    end
  end

  @doc false
  def process_worker_heartbeat(attrs) do
    attrs = normalize_map(Map.new(attrs))

    case Store.fetch_worker_registration(Map.fetch!(attrs, :worker_id)) do
      nil ->
        {:error, :unknown_worker}

      registration ->
        attributes =
          registration.attributes
          |> Map.new()
          |> Map.merge(Map.get(attrs, :attributes, %{}) |> Map.new())
          |> Map.put_new(
            "worker_pool_id",
            Map.get(attrs, :worker_pool_id, Map.get(registration.attributes, :worker_pool_id, "shared"))
          )
          |> Map.put_new(
            "isolation_tier",
            Map.get(attrs, :isolation_tier, Map.get(registration.attributes, :isolation_tier, "tier_a"))
          )

        {:ok,
         Store.upsert_worker_registration(%{
           worker_id: registration.worker_id,
           worker_kind: registration.worker_kind,
           worker_version: registration.worker_version,
           supported_contract_versions: registration.supported_contract_versions,
           advertised_capacity: registration.advertised_capacity,
           available_capacity:
             Map.get(attrs, :available_capacity, registration.available_capacity),
           attributes: attributes,
           status: "active",
           last_seen_at: Map.get(attrs, :observed_at, now())
         })}
    end
  end

  @doc false
  def process_worker_callback(kind, worker_kind, payload, headers) do
    ingest(kind, worker_kind, payload, headers)
  end

  def published_messages, do: InMemoryTransport.published_messages()
  def execution(execution_id), do: Store.fetch_execution(execution_id)
  def worker_registration(worker_id), do: Store.fetch_worker_registration(worker_id)

  def reset! do
    InMemoryTransport.reset!()
    :ok
  end

  defp flush_outbox_row(row) do
    case row.event_type do
      "policy.evaluated" ->
        publish_policy_dispatch(row)

      "approval.granted" ->
        publish_approved_dispatch(row)

      "action.cancel_requested" ->
        publish_cancel(row)

      unsupported ->
        Store.release_outbox(row.outbox_id)
        {:error, {:unsupported_outbox_event, unsupported}}
    end
  rescue
    error ->
      Store.release_outbox(row.outbox_id)
      {:error, {row.outbox_id, Exception.message(error)}}
  end

  defp publish_policy_dispatch(row) do
    payload = normalize_map(row.payload)

    case fetch_value(payload, :decision) do
      decision when decision in ["allow", "allow_with_constraints"] ->
        publish_dispatch(row, payload_for_action!(row.session_id, fetch_value(payload, :action_id)))

      _other ->
        Store.mark_outbox_published(row.outbox_id)
        {:ok, %{outbox_id: row.outbox_id, action_id: fetch_value(payload, :action_id), skipped: true}}
    end
  end

  defp publish_approved_dispatch(row) do
    payload = normalize_map(row.payload)
    publish_dispatch(row, payload_for_action!(row.session_id, fetch_value(payload, :action_id)))
  end

  defp publish_dispatch(row, payload) do
    headers = normalize_headers(row.headers)
    session_ref = session_ref_from_headers(headers)

    worker_kind =
      fetch_value(payload, :worker_kind) || derive_worker_kind(fetch_value(payload, :tool_id))

    timeout_policy = TransportTopology.timeout_class(fetch_value(payload, :timeout_class))

    accept_deadline =
      resolve_deadline(fetch_value(payload, :accept_deadline), timeout_policy.accept_seconds)

    soft_deadline =
      resolve_deadline(fetch_value(payload, :soft_deadline), timeout_policy.soft_seconds)

    hard_deadline =
      resolve_deadline(fetch_value(payload, :hard_deadline), timeout_policy.hard_seconds)

    execution_id = deterministic_execution_id(row.session_id, fetch_value(payload, :action_id))
    contract_version = Map.get(headers, "x-aegis-contract-version", "v1")
    isolation_tier = Map.get(headers, "x-aegis-isolation-tier", "tier_a")
    route_key = fetch_value(payload, :dispatch_route_key) || "shared"
    dispatch_subject = TransportTopology.routed_subject_for(:dispatch, worker_kind, route_key)
    action_scope = %{
      tenant_id: session_ref.tenant_id,
      workspace_id: session_ref.workspace_id,
      isolation_tier: isolation_tier
    }
    action_attrs = %{
      action_id: fetch_value(payload, :action_id),
      tool_id: fetch_value(payload, :tool_id),
      worker_kind: worker_kind,
      mutating: Map.get(payload, :mutating, false)
    }

    case AdmissionControl.admit_dispatch(action_scope, action_attrs) do
      :ok ->
        execution =
          with :ok <- ensure_outbox_scope(row, session_ref) do
            Store.upsert_execution(%{
              execution_id: execution_id,
              tenant_id: session_ref.tenant_id,
              workspace_id: session_ref.workspace_id,
              session_id: row.session_id,
              action_id: fetch_value(payload, :action_id),
              worker_kind: worker_kind,
              contract_version: contract_version,
              dispatch_subject: dispatch_subject,
              trace_id: fetch_value(payload, :trace_id) || Map.get(headers, "x-aegis-trace-id"),
              idempotency_key: fetch_value(payload, :idempotency_key),
              isolation_tier: isolation_tier,
              status: "dispatched",
              lease_epoch: session_ref.lease_epoch,
              accept_deadline: accept_deadline,
              soft_deadline: soft_deadline,
              hard_deadline: hard_deadline,
              last_payload: payload
            })
          end

        message = %{
          ref: session_ref,
          contract_version: contract_version,
          execution_id: execution.execution_id,
          action_id: execution.action_id,
          tool_id: fetch_value(payload, :tool_id),
          tool_schema_version: fetch_value(payload, :tool_schema_version),
          capability_token: fetch_value(payload, :capability_token_ref) || "",
          trace_id: execution.trace_id || "",
          idempotency_key: execution.idempotency_key || "",
          isolation_tier: isolation_tier,
          input: fetch_value(payload, :input) || %{},
          accept_deadline: iso8601(accept_deadline),
          soft_deadline: iso8601(soft_deadline),
          hard_deadline: iso8601(hard_deadline)
        }

        with execution when is_map(execution) <- execution,
             {:ok, _published} <- InMemoryTransport.publish(dispatch_subject, message, headers),
             {:ok, _runtime_result} <-
               dispatch_runtime_command(
                 session_ref,
                 {:dispatch_action,
                  %{
                    action_id: execution.action_id,
                    execution_id: execution.execution_id,
                    worker_kind: worker_kind,
                    isolation_tier: isolation_tier,
                    worker_pool_id: fetch_value(payload, :worker_pool_id),
                    dispatch_route_key: route_key,
                    worker_subject: dispatch_subject,
                    accept_deadline: iso8601(accept_deadline),
                    soft_deadline: iso8601(soft_deadline),
                    hard_deadline: iso8601(hard_deadline),
                    contract_version: contract_version,
                    capability_token_required: present?(fetch_value(payload, :capability_token_ref)),
                    trace_id: execution.trace_id,
                    idempotency_key: execution.idempotency_key
                  }},
                 actor_kind: "system",
                 actor_id: "execution_bridge",
                 trace_id: execution.trace_id,
                 idempotency_key: execution.idempotency_key,
                 correlation_id: execution.execution_id
               ) do
          Store.mark_outbox_published(row.outbox_id)

          {:ok,
           %{
             outbox_id: row.outbox_id,
             execution_id: execution.execution_id,
             subject: dispatch_subject
           }}
        end

      {:error, {:quota_exceeded, quota_class, details}} ->
        Store.release_outbox(row.outbox_id)

        {:ok,
         %{
           outbox_id: row.outbox_id,
           action_id: fetch_value(payload, :action_id),
           deferred: true,
           quota_class: quota_class,
           quota: details
         }}
    end
  end

  defp payload_for_action!(session_id, action_id) do
    session_state = Runtime.snapshot(session_id)

    action =
      Enum.find(session_state.durable.action_ledger, &(&1.action_id == action_id)) ||
        raise ArgumentError, "unknown action #{inspect(action_id)} for dispatch"

    if action.status in ["denied", "approval_expired"] do
      raise ArgumentError, "action #{inspect(action_id)} is not dispatchable"
    end

    if Map.get(action, :mutating, false) and not present?(Map.get(action, :capability_token_ref)) do
      raise ArgumentError, "mutating action #{inspect(action_id)} is missing a capability token"
    end

    %{
      action_id: action.action_id,
      tool_id: action.tool_id,
      tool_schema_version: action.tool_schema_version,
      worker_kind: action.worker_kind,
      isolation_tier: Map.get(action, :isolation_tier, "tier_a"),
      worker_pool_id: Map.get(action, :worker_pool_id),
      dispatch_route_key: Map.get(action, :dispatch_route_key, "shared"),
      input: action.input,
      risk_class: action.risk_class,
      dangerous_action_class: Map.get(action, :dangerous_action_class),
      idempotency_class: action.idempotency_class,
      idempotency_key: action.idempotency_key,
      timeout_class: action.timeout_class,
      mutating: action.mutating,
      accept_deadline: action.accept_deadline,
      soft_deadline: action.soft_deadline,
      hard_deadline: action.hard_deadline,
      trace_id: action.trace_id,
      capability_token_ref: Map.get(action, :capability_token_ref),
      approved_argument_digest: Map.get(action, :approved_argument_digest)
    }
  end

  defp publish_cancel(row) do
    payload = normalize_map(row.payload)
    headers = normalize_headers(row.headers)
    session_ref = session_ref_from_headers(headers)

    execution =
      Store.fetch_execution(fetch_value(payload, :execution_id), session_ref) ||
        Store.fetch_execution_by_action(
          row.session_id,
          fetch_value(payload, :action_id),
          session_ref
        ) ||
        raise ArgumentError, "unknown execution for cancel #{inspect(payload)}"

    cancel_subject = routed_cancel_subject(execution)
    cancel_requested_at = resolve_deadline(fetch_value(payload, :cancel_requested_at), 0)

    with {:ok, _published} <-
           InMemoryTransport.publish(
             cancel_subject,
             %{
               ref: session_ref,
               execution_id: execution.execution_id,
               action_id: execution.action_id,
               reason: fetch_value(payload, :reason),
               cancel_requested_at: iso8601(cancel_requested_at)
             },
             headers
           ) do
      Store.mark_execution_cancel_requested(execution.execution_id, %{
        reason: fetch_value(payload, :reason),
        cancel_requested_at: cancel_requested_at
      })

      Store.mark_outbox_published(row.outbox_id)

      {:ok,
       %{outbox_id: row.outbox_id, execution_id: execution.execution_id, subject: cancel_subject}}
    end
  end

  defp ingest(kind, worker_kind, payload, headers) do
    payload = normalize_map(Map.new(payload))
    headers = normalize_headers(headers)
    session_ref = normalize_session_ref(fetch_value(payload, :ref))
    execution_id = fetch_value(payload, :execution_id)

    with :ok <- ensure_expected_subject(kind, worker_kind),
         :ok <- ensure_header_scope(headers, session_ref),
         :ok <- ensure_session_started(session_ref),
         execution when not is_nil(execution) <- Store.fetch_execution(execution_id, session_ref),
         :ok <- ensure_execution_scope(execution, session_ref) do
      if terminal_execution?(execution) do
        handle_terminal_callback(kind, execution, payload, headers, session_ref)
      else
        do_ingest(kind, execution, worker_kind, payload, headers, session_ref)
      end
    else
      nil -> {:error, :unknown_execution}
      {:error, reason} -> {:error, reason}
    end
  end

  defp do_ingest(:accepted, execution, _worker_kind, payload, _headers, _session_ref) do
    {:ok,
     Store.mark_execution_accepted(execution.execution_id, %{
       worker_id: fetch_value(payload, :worker_id),
       accepted_at: fetch_value(payload, :accepted_at)
     })}
  end

  defp do_ingest(:progress, execution, _worker_kind, payload, headers, session_ref) do
    case Store.mark_execution_progress(execution.execution_id, %{
           progress_kind: fetch_value(payload, :progress_kind),
           progress_seq: fetch_value(payload, :progress_seq),
           progress: fetch_value(payload, :progress) || %{},
           observed_at: fetch_value(payload, :observed_at),
           worker_id: execution.worker_id
         }) do
      {:duplicate, updated} ->
        {:ok, updated}

      {:updated, _updated} ->
        dispatch_runtime_command(
          session_ref,
          {:record_action_progress,
           %{
             action_id: execution.action_id,
             execution_id: execution.execution_id,
             progress_kind: fetch_value(payload, :progress_kind),
             progress_seq: fetch_value(payload, :progress_seq),
             observed_at: fetch_value(payload, :observed_at),
             worker_id: execution.worker_id,
             progress: fetch_value(payload, :progress) || %{},
             artifact_refs: []
           }},
          actor_kind: "worker",
          actor_id: execution.worker_id || "worker",
          trace_id: execution.trace_id || Map.get(headers, "x-aegis-trace-id"),
          idempotency_key: execution.idempotency_key,
          correlation_id: execution.execution_id
        )
    end
  end

  defp do_ingest(:heartbeat, execution, _worker_kind, payload, _headers, _session_ref) do
    {:ok,
     Store.mark_execution_heartbeat(execution.execution_id, %{
       heartbeat_seq: fetch_value(payload, :heartbeat_seq),
       observed_at: fetch_value(payload, :observed_at)
     })}
  end

  defp do_ingest(:completed, execution, _worker_kind, payload, headers, session_ref) do
    completed_at = fetch_value(payload, :completed_at)

    updated =
      Store.mark_execution_completed(execution.execution_id, %{
        completed_at: completed_at,
        normalized_result: fetch_value(payload, :normalized_result) || %{},
        raw_result_artifact_id: fetch_value(payload, :raw_result_artifact_id)
      })

    with {:ok, _runtime_result} <-
           dispatch_runtime_command(
             session_ref,
             {:record_action_succeeded,
              %{
                action_id: execution.action_id,
                execution_id: execution.execution_id,
                completed_at: completed_at,
                normalized_result: fetch_value(payload, :normalized_result) || %{},
                raw_result_artifact_id: fetch_value(payload, :raw_result_artifact_id) || ""
              }},
             actor_kind: "worker",
             actor_id: updated.worker_id || "worker",
             trace_id: updated.trace_id || Map.get(headers, "x-aegis-trace-id"),
             idempotency_key: updated.idempotency_key,
             correlation_id: updated.execution_id
           ),
         :ok <-
           maybe_register_artifact(
             session_ref,
             execution.action_id,
             fetch_value(payload, :raw_result_artifact_id),
             "worker_result",
             completed_at,
             updated.trace_id
           ) do
      {:ok, updated}
    end
  end

  defp do_ingest(:failed, execution, _worker_kind, payload, headers, session_ref) do
    failed_at = fetch_value(payload, :failed_at)

    updated =
      Store.mark_execution_failed(execution.execution_id, %{
        error_code: fetch_value(payload, :error_code),
        error_class: fetch_value(payload, :error_class),
        retryable: fetch_value(payload, :retryable),
        safe_to_retry: fetch_value(payload, :safe_to_retry),
        compensation_possible: fetch_value(payload, :compensation_possible),
        uncertain_side_effect: fetch_value(payload, :uncertain_side_effect),
        details_artifact_id: fetch_value(payload, :details_artifact_id),
        failed_at: failed_at
      })

    with {:ok, _runtime_result} <-
           dispatch_runtime_command(
             session_ref,
             {:record_action_failed,
              %{
                action_id: execution.action_id,
                execution_id: execution.execution_id,
                error_code: fetch_value(payload, :error_code),
                error_class: fetch_value(payload, :error_class),
                retryable: fetch_value(payload, :retryable),
                safe_to_retry: fetch_value(payload, :safe_to_retry),
                compensation_possible: fetch_value(payload, :compensation_possible),
                uncertain_side_effect: fetch_value(payload, :uncertain_side_effect),
                details_artifact_id: fetch_value(payload, :details_artifact_id),
                failed_at: failed_at
              }},
             actor_kind: "worker",
             actor_id: updated.worker_id || "worker",
             trace_id: updated.trace_id || Map.get(headers, "x-aegis-trace-id"),
             idempotency_key: updated.idempotency_key,
             correlation_id: updated.execution_id
           ),
         :ok <-
           maybe_register_artifact(
             session_ref,
             execution.action_id,
             fetch_value(payload, :details_artifact_id),
             "worker_failure_details",
             failed_at,
             updated.trace_id
           ) do
      {:ok, updated}
    end
  end

  defp do_ingest(:cancelled, execution, _worker_kind, payload, headers, session_ref) do
    cancelled_at = fetch_value(payload, :cancelled_at)

    updated =
      Store.mark_execution_cancelled(execution.execution_id, %{
        worker_id: fetch_value(payload, :worker_id),
        reason: fetch_value(payload, :reason),
        cancelled_at: cancelled_at
      })

    with {:ok, _runtime_result} <-
           dispatch_runtime_command(
             session_ref,
             {:record_action_cancelled,
              %{
                action_id: execution.action_id,
                execution_id: execution.execution_id,
                worker_id: fetch_value(payload, :worker_id),
                reason: fetch_value(payload, :reason),
                cancelled_at: cancelled_at
              }},
             actor_kind: "worker",
             actor_id: updated.worker_id || "worker",
             trace_id: updated.trace_id || Map.get(headers, "x-aegis-trace-id"),
             idempotency_key: updated.idempotency_key,
             correlation_id: updated.execution_id
           ) do
      {:ok, updated}
    end
  end

  defp scan_execution(execution, reference_time, heartbeat_policy) do
    cond do
      execution.status == "dispatched" and stale_accept_deadline?(execution, reference_time) ->
        timeout_execution(execution)

      execution.status in ["accepted", "in_progress", "cancellation_requested"] and
          stale_hard_deadline?(execution, reference_time) ->
        hard_timeout_execution(execution)

      execution.status in ["accepted", "in_progress", "cancellation_requested"] and
          stale_heartbeat?(execution, reference_time, heartbeat_policy) ->
        mark_worker_lost(execution)

      true ->
        nil
    end
  end

  defp timeout_execution(execution) do
    session_ref = session_ref_for_execution!(execution)
    failed_at = now()

    updated =
      Store.mark_execution_failed(execution.execution_id, %{
        error_code: "accept_deadline_exceeded",
        error_class: "transport_timeout",
        retryable: true,
        safe_to_retry: true,
        compensation_possible: false,
        uncertain_side_effect: false,
        failed_at: failed_at
      })

    with {:ok, _runtime_result} <-
           dispatch_runtime_command(
             session_ref,
             {:record_action_failed,
              %{
                action_id: execution.action_id,
                execution_id: execution.execution_id,
                error_code: "accept_deadline_exceeded",
                error_class: "transport_timeout",
                retryable: true,
                safe_to_retry: true,
                compensation_possible: false,
                uncertain_side_effect: false,
                failed_at: iso8601(failed_at)
              }},
             actor_kind: "system",
             actor_id: "execution_bridge_timeout_scanner",
             trace_id: updated.trace_id,
             idempotency_key: updated.idempotency_key,
             correlation_id: updated.execution_id
           ) do
      {:ok, {:accept_timeout, updated.execution_id}}
    end
  end

  defp hard_timeout_execution(execution) do
    session_ref = session_ref_for_execution!(execution)
    failed_at = now()

    updated =
      Store.mark_execution_failed(execution.execution_id, %{
        error_code: "hard_deadline_exceeded",
        error_class: "execution_timeout",
        retryable: false,
        safe_to_retry: false,
        compensation_possible: false,
        uncertain_side_effect: true,
        failed_at: failed_at
      })

    with {:ok, _runtime_result} <-
           dispatch_runtime_command(
             session_ref,
             {:record_action_failed,
              %{
                action_id: execution.action_id,
                execution_id: execution.execution_id,
                error_code: "hard_deadline_exceeded",
                error_class: "execution_timeout",
                retryable: false,
                safe_to_retry: false,
                compensation_possible: false,
                uncertain_side_effect: true,
                failed_at: iso8601(failed_at)
              }},
             actor_kind: "system",
             actor_id: "execution_bridge_timeout_scanner",
             trace_id: updated.trace_id,
             idempotency_key: updated.idempotency_key,
             correlation_id: updated.execution_id
           ) do
      {:ok, {:hard_timeout, updated.execution_id}}
    end
  end

  defp mark_worker_lost(execution) do
    session_ref = session_ref_for_execution!(execution)

    updated =
      Store.mark_execution_lost(execution.execution_id, %{
        worker_id: execution.worker_id || "unknown-worker",
        action_id: execution.action_id,
        reason: "missed_action_heartbeat",
        last_heartbeat_at: maybe_iso8601(execution.last_heartbeat_at),
        uncertain_side_effect: true
      })

    with {:ok, _runtime_result} <-
           dispatch_runtime_command(
             session_ref,
             {:record_worker_lost,
              %{
                action_id: execution.action_id,
                execution_id: execution.execution_id,
                worker_id: updated.worker_id || "unknown-worker",
                reason: "missed_action_heartbeat",
                last_heartbeat_at: maybe_iso8601(execution.last_heartbeat_at)
              }},
             actor_kind: "system",
             actor_id: "execution_bridge_timeout_scanner",
             trace_id: updated.trace_id,
             idempotency_key: updated.idempotency_key,
             correlation_id: updated.execution_id
           ) do
      {:ok, {:worker_lost, updated.execution_id}}
    end
  end

  defp handle_terminal_callback(kind, execution, payload, headers, session_ref) do
    cond do
      not terminal_callback?(kind) ->
        {:ok, :duplicate_terminal_callback}

      execution.status in ["uncertain", "lost"] ->
        {:ok, :duplicate_terminal_callback}

      terminal_kind_for_status(execution.status) == kind ->
        {:ok, :duplicate_terminal_callback}

      true ->
        classify_conflicting_terminal_callback(kind, execution, payload, headers, session_ref)
    end
  end

  defp classify_conflicting_terminal_callback(kind, execution, payload, headers, session_ref) do
    failed_at = duplicate_terminal_occurred_at(kind, payload)
    artifact_id = duplicate_terminal_artifact_id(kind, payload)
    artifact_kind = duplicate_terminal_artifact_kind(kind)

    updated =
      Store.mark_execution_failed(execution.execution_id, %{
        error_code: "duplicate_terminal_callback",
        error_class: "duplicate_execution",
        retryable: false,
        safe_to_retry: false,
        compensation_possible: false,
        uncertain_side_effect: true,
        details_artifact_id: artifact_id,
        failed_at: failed_at
      })

    with {:ok, _runtime_result} <-
           dispatch_runtime_command(
             session_ref,
             {:record_action_failed,
              %{
                action_id: execution.action_id,
                execution_id: execution.execution_id,
                error_code: "duplicate_terminal_callback",
                error_class: "duplicate_execution",
                retryable: false,
                safe_to_retry: false,
                compensation_possible: false,
                uncertain_side_effect: true,
                details_artifact_id: artifact_id,
                failed_at: failed_at
              }},
             actor_kind: "worker",
             actor_id: updated.worker_id || "worker",
             trace_id: updated.trace_id || Map.get(headers, "x-aegis-trace-id"),
             idempotency_key: updated.idempotency_key,
             correlation_id: updated.execution_id
           ),
         :ok <-
           maybe_register_artifact(
             session_ref,
             execution.action_id,
             artifact_id,
             artifact_kind,
             failed_at,
             updated.trace_id
           ) do
      {:ok, updated}
    end
  end

  defp maybe_register_artifact(
         _session_ref,
         _action_id,
         artifact_id,
         _artifact_kind,
         _recorded_at,
         _trace_id
       )
       when artifact_id in [nil, ""] do
    :ok
  end

  defp maybe_register_artifact(
         session_ref,
         action_id,
         artifact_id,
         artifact_kind,
         recorded_at,
         trace_id
       ) do
    dispatch_runtime_command(
      session_ref,
      {:register_artifact,
       %{
         artifact_id: artifact_id,
         artifact_kind: artifact_kind,
         storage_ref: "artifact://#{artifact_id}",
         recorded_at: recorded_at,
         action_id: action_id
       }},
      actor_kind: "worker",
      actor_id: "execution_bridge",
      trace_id: trace_id,
      correlation_id: action_id
    )
    |> case do
      {:ok, _} -> :ok
      {:error, reason} -> {:error, reason}
    end
  end

  defp dispatch_runtime_command(session_ref, command, opts) do
    with :ok <- ensure_session_started(session_ref),
         {:ok, lease} <- Runtime.lease(session_ref.session_id) do
      runtime_opts =
        opts
        |> Keyword.new()
        |> Keyword.put_new(:owner_node, lease.owner_node)
        |> Keyword.put_new(:lease_epoch, lease.lease_epoch)

      Runtime.dispatch(session_ref.session_id, command, runtime_opts)
    end
  end

  defp ensure_session_started(session_ref) do
    case Runtime.tree_pid(session_ref.session_id) do
      nil ->
        case Runtime.start_session(%{
               session_id: session_ref.session_id,
               tenant_id: session_ref.tenant_id,
               workspace_id: session_ref.workspace_id,
               requested_by: "execution_bridge",
               session_kind: "browser_operation"
             }) do
          {:ok, _pid} -> :ok
          {:error, {:already_started, _pid}} -> :ok
          {:error, {:already_present, _pid}} -> :ok
          other -> other
        end

      _pid ->
        :ok
    end
  end

  defp session_ref_for_execution!(execution) do
    case session_ref_for_session(execution.session_id) do
      {:ok, session_ref} ->
        session_ref

      {:error, reason} ->
        raise "unable to build session ref for #{execution.execution_id}: #{inspect(reason)}"
    end
  end

  defp session_ref_for_session(session_id) do
    with {:ok, replay} <- Runtime.historical_replay(session_id) do
      {:ok,
       %{
         tenant_id: replay.replay_state.tenant_id,
         workspace_id: replay.replay_state.workspace_id,
         session_id: replay.replay_state.session_id,
         lease_epoch: replay.replay_state.lease_epoch
       }}
    end
  end

  defp ensure_outbox_scope(row, session_ref) do
    cond do
      row.tenant_id != session_ref.tenant_id ->
        {:error,
         {:scope_mismatch, :tenant_id,
          %{expected: row.tenant_id, actual: session_ref.tenant_id, session_id: row.session_id}}}

      row.workspace_id != session_ref.workspace_id ->
        {:error,
         {:scope_mismatch, :workspace_id,
          %{expected: row.workspace_id, actual: session_ref.workspace_id, session_id: row.session_id}}}

      true ->
        :ok
    end
  end

  defp ensure_execution_scope(execution, session_ref) do
    cond do
      execution.tenant_id != session_ref.tenant_id ->
        {:error,
         {:scope_mismatch, :tenant_id,
          %{expected: execution.tenant_id, actual: session_ref.tenant_id, execution_id: execution.execution_id}}}

      execution.workspace_id != session_ref.workspace_id ->
        {:error,
         {:scope_mismatch, :workspace_id,
          %{expected: execution.workspace_id, actual: session_ref.workspace_id, execution_id: execution.execution_id}}}

      true ->
        :ok
    end
  end

  defp ensure_header_scope(headers, session_ref) do
    tenant_id = Map.get(headers, "x-aegis-tenant-id")
    workspace_id = Map.get(headers, "x-aegis-workspace-id")

    cond do
      present?(tenant_id) and tenant_id != session_ref.tenant_id ->
        {:error,
         {:scope_mismatch, :tenant_id,
          %{expected: session_ref.tenant_id, actual: tenant_id, session_id: session_ref.session_id}}}

      present?(workspace_id) and workspace_id != session_ref.workspace_id ->
        {:error,
         {:scope_mismatch, :workspace_id,
          %{expected: session_ref.workspace_id, actual: workspace_id, session_id: session_ref.session_id}}}

      true ->
        :ok
    end
  end

  defp ensure_expected_subject(kind, worker_kind) do
    expected_names =
      MapSet.new(["accepted", "progress", "completed", "failed", "cancelled", "heartbeat"])

    if MapSet.member?(expected_names, Atom.to_string(kind)) and is_binary(worker_kind) do
      TransportTopology.subject_for(kind, worker_kind)
      :ok
    else
      {:error, {:unknown_transport_callback, kind, worker_kind}}
    end
  end

  defp session_ref_from_headers(headers) do
    %{
      tenant_id: Map.fetch!(headers, "x-aegis-tenant-id"),
      workspace_id: Map.fetch!(headers, "x-aegis-workspace-id"),
      session_id: Map.fetch!(headers, "x-aegis-session-id"),
      lease_epoch:
        Map.fetch!(headers, "x-aegis-lease-epoch") |> to_string() |> String.to_integer()
    }
  end

  defp normalize_session_ref(session_ref) do
    ref = normalize_map(session_ref)

    %{
      tenant_id: fetch_value(ref, :tenant_id),
      workspace_id: fetch_value(ref, :workspace_id),
      session_id: fetch_value(ref, :session_id),
      lease_epoch: fetch_value(ref, :lease_epoch)
    }
  end

  defp normalize_headers(headers) do
    headers
    |> Map.new()
    |> Enum.map(fn {key, value} -> {to_string(key), value} end)
    |> Enum.into(%{})
  end

  defp normalize_map(%_{} = value), do: value

  defp normalize_map(value) when is_map(value) do
    value
    |> Enum.map(fn {key, item} -> {normalize_key(key), normalize_map(item)} end)
    |> Enum.into(%{})
  end

  defp normalize_map(value) when is_list(value), do: Enum.map(value, &normalize_map/1)
  defp normalize_map(value), do: value

  defp normalize_key(key) when is_atom(key), do: key

  defp normalize_key(key) when is_binary(key) do
    try do
      String.to_existing_atom(key)
    rescue
      ArgumentError -> key
    end
  end

  defp derive_worker_kind(tool_id) when is_binary(tool_id) do
    tool_id
    |> String.split(".", parts: 2)
    |> List.first()
  end

  defp deterministic_execution_id(session_id, action_id) do
    suffix =
      :crypto.hash(:sha256, "#{session_id}:#{action_id}")
      |> Base.encode16(case: :lower)
      |> binary_part(0, 16)

    "exec-#{suffix}"
  end

  defp resolve_deadline(nil, offset_seconds), do: DateTime.add(now(), offset_seconds, :second)
  defp resolve_deadline(value, _offset_seconds) when is_binary(value), do: parse_datetime(value)
  defp resolve_deadline(%DateTime{} = value, _offset_seconds), do: value

  defp stale_accept_deadline?(execution, reference_time) do
    execution.accept_deadline != nil and
      DateTime.compare(execution.accept_deadline, reference_time) != :gt and
      execution.accepted_at == nil
  end

  defp stale_heartbeat?(execution, reference_time, heartbeat_policy) do
    last_heartbeat_at = execution.last_heartbeat_at || execution.accepted_at

    if last_heartbeat_at == nil do
      false
    else
      deadline =
        DateTime.add(
          last_heartbeat_at,
          heartbeat_policy.default_interval_seconds *
            heartbeat_policy.missed_heartbeats_before_loss,
          :second
        )

      DateTime.compare(deadline, reference_time) != :gt
    end
  end

  defp stale_hard_deadline?(execution, reference_time) do
    execution.hard_deadline != nil and
      DateTime.compare(execution.hard_deadline, reference_time) != :gt
  end

  defp terminal_execution?(execution) do
    MapSet.member?(@terminal_statuses, execution.status)
  end

  defp terminal_callback?(:completed), do: true
  defp terminal_callback?(:failed), do: true
  defp terminal_callback?(:cancelled), do: true
  defp terminal_callback?(_kind), do: false

  defp terminal_kind_for_status("succeeded"), do: :completed
  defp terminal_kind_for_status("failed"), do: :failed
  defp terminal_kind_for_status("cancelled"), do: :cancelled
  defp terminal_kind_for_status(_status), do: :uncertain

  defp duplicate_terminal_occurred_at(:completed, payload),
    do: fetch_value(payload, :completed_at) || iso8601(now())

  defp duplicate_terminal_occurred_at(:failed, payload),
    do: fetch_value(payload, :failed_at) || iso8601(now())

  defp duplicate_terminal_occurred_at(:cancelled, payload),
    do: fetch_value(payload, :cancelled_at) || iso8601(now())

  defp duplicate_terminal_artifact_id(:completed, payload),
    do: fetch_value(payload, :raw_result_artifact_id)

  defp duplicate_terminal_artifact_id(:failed, payload),
    do: fetch_value(payload, :details_artifact_id)

  defp duplicate_terminal_artifact_id(:cancelled, _payload), do: nil

  defp duplicate_terminal_artifact_kind(:completed), do: "worker_result"
  defp duplicate_terminal_artifact_kind(:failed), do: "worker_failure_details"
  defp duplicate_terminal_artifact_kind(:cancelled), do: nil

  defp publish_worker_callback(kind, worker_kind, payload, headers) do
    payload = normalize_map(Map.new(payload))
    headers = normalize_headers(headers)
    subject = TransportTopology.subject_for(kind, worker_kind)

    with {:ok, _message} <- publish_transport(subject, payload, headers) do
      {:ok, Store.fetch_execution(fetch_value(payload, :execution_id))}
    end
  end

  defp publish_transport(subject, payload, headers) do
    case InMemoryTransport.publish(subject, payload, headers) do
      {:ok, message} -> {:ok, message}
      {:error, reason, _message} -> {:error, reason}
    end
  end

  defp registry_headers do
    %{"x-aegis-contract-version" => "v1"}
  end

  defp routed_cancel_subject(execution) do
    execution.dispatch_subject
    |> to_string()
    |> String.replace(".command.dispatch.", ".command.cancel.")
  end

  defp fetch_value(map, key) do
    Map.get(map, key) || Map.get(map, to_string(key))
  end

  defp present?(value), do: value not in [nil, ""]

  defp parse_datetime(%DateTime{} = value), do: value

  defp parse_datetime(value) when is_binary(value) do
    {:ok, datetime, _offset} = DateTime.from_iso8601(value)
    datetime
  end

  defp maybe_iso8601(nil), do: nil
  defp maybe_iso8601(%DateTime{} = value), do: iso8601(value)
  defp maybe_iso8601(value) when is_binary(value), do: value

  defp iso8601(%DateTime{} = value), do: DateTime.to_iso8601(DateTime.truncate(value, :second))
  defp iso8601(value) when is_binary(value), do: value

  defp now, do: DateTime.utc_now() |> DateTime.truncate(:second)
end
