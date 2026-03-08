defmodule Aegis.ExecutionBridgeTest do
  use ExUnit.Case, async: false

  alias Aegis.Events
  alias Aegis.ExecutionBridge
  alias Aegis.ExecutionBridge.Guardrails
  alias Aegis.Runtime

  setup do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(Aegis.Repo)
    Ecto.Adapters.SQL.Sandbox.mode(Aegis.Repo, {:shared, self()})

    Events.reset!()
    ExecutionBridge.reset!()

    session_id = "bridge-session-#{System.unique_integer([:positive])}"

    {:ok, tree_pid} =
      Runtime.start_session(%{
        session_id: session_id,
        tenant_id: "tenant-bridge",
        workspace_id: "workspace-bridge",
        requested_by: "bridge-suite",
        session_kind: "browser_operation"
      })

    {:ok, lease} = Runtime.lease(session_id)

    assert {:ok, _} =
             Runtime.dispatch(
               session_id,
               {:activate, %{owner_node: lease.owner_node, lease_epoch: lease.lease_epoch}},
               owner_node: lease.owner_node,
               lease_epoch: lease.lease_epoch
             )

    on_exit(fn ->
      if Process.alive?(tree_pid) do
        Process.exit(tree_pid, :shutdown)
      end
    end)

    %{session_id: session_id}
  end

  test "registers workers and tracks capacity heartbeats" do
    assert {:ok, registration} =
             ExecutionBridge.register_worker(%{
               worker_id: "worker-browser-1",
               worker_kind: "browser",
               worker_version: "0.4.0",
               supported_contract_versions: ["v1"],
               advertised_capacity: 4,
               attributes: %{"region" => "eu-central"}
             })

    assert registration.available_capacity == 4
    assert registration.status == "active"

    assert {:ok, heartbeat} =
             ExecutionBridge.worker_heartbeat(%{
               worker_id: "worker-browser-1",
               observed_at: "2026-03-08T13:05:00Z",
               available_capacity: 2,
               attributes: %{"region" => "eu-central", "load" => "50%"}
             })

    assert heartbeat.available_capacity == 2
    assert heartbeat.attributes.region == "eu-central"
    assert heartbeat.attributes.load == "50%"

    [registered_message, heartbeat_message] = ExecutionBridge.published_messages()
    assert registered_message.subject == "aegis.v1.registry.register.browser"
    assert registered_message.ack_status == :ack
    assert heartbeat_message.subject == "aegis.v1.registry.heartbeat.browser"
    assert heartbeat_message.ack_status == :ack
  end

  test "dispatches committed action intent through the bridge with trace headers", %{
    session_id: session_id
  } do
    {:ok, lease} = Runtime.lease(session_id)

    assert {:ok, _result} =
             Runtime.dispatch(
               session_id,
               {:request_action,
                %{
                  action_id: "action-dispatch-1",
                  tool_id: "browser.navigate",
                  tool_schema_version: "v1",
                  worker_kind: "browser",
                  input: %{url: "https://example.com"},
                  risk_class: "read_only",
                  idempotency_class: "idempotent",
                  timeout_class: "short",
                  mutating: false
                }},
               owner_node: lease.owner_node,
               lease_epoch: lease.lease_epoch,
               trace_id: "trace-dispatch-1",
               idempotency_key: "idem-dispatch-1"
             )

    assert [{:ok, dispatch_result}] = ExecutionBridge.flush_dispatches()

    [published] = ExecutionBridge.published_messages()
    assert published.subject == "aegis.v1.command.dispatch.browser"
    assert published.ack_status == :unconsumed
    assert published.payload.action_id == "action-dispatch-1"
    assert published.payload.trace_id == "trace-dispatch-1"
    assert published.headers["x-aegis-trace-id"] == "trace-dispatch-1"
    assert published.headers["x-aegis-tenant-id"] == "tenant-bridge"
    assert published.headers["x-aegis-workspace-id"] == "workspace-bridge"
    assert published.headers["x-aegis-session-id"] == session_id
    assert published.headers["x-aegis-lease-epoch"] == Integer.to_string(lease.lease_epoch)
    assert published.headers["x-aegis-contract-version"] == "v1"
    assert published.headers["x-aegis-isolation-tier"] == "tier_a"

    execution = ExecutionBridge.execution(dispatch_result.execution_id)
    assert execution.status == "dispatched"
    assert execution.worker_kind == "browser"
    assert execution.trace_id == "trace-dispatch-1"
    assert execution.idempotency_key == "idem-dispatch-1"

    dispatched_event =
      Runtime.events(session_id)
      |> Enum.find(&(&1.type == "action.dispatched"))

    assert dispatched_event.trace_id == "trace-dispatch-1"
    assert dispatched_event.idempotency_key == "idem-dispatch-1"

    outbox_row =
      Events.outbox(session_id)
      |> Enum.find(&(&1.event_type == "policy.evaluated"))

    assert outbox_row.status == "published"
    assert outbox_row.headers["x-aegis-trace-id"] == "trace-dispatch-1"
  end

  test "ingests progress and completion callbacks and registers worker artifacts", %{
    session_id: session_id
  } do
    execution_id = dispatch_action!(session_id, "action-complete-1", "trace-complete-1")
    session_ref = session_ref(session_id)

    assert {:ok, accepted} =
             ExecutionBridge.accept_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               worker_id: "worker-browser-1",
               accepted_at: "2026-03-08T13:10:00Z"
             })

    assert accepted.status == "accepted"

    assert {:ok, _progress} =
             ExecutionBridge.progress_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               action_id: "action-complete-1",
               progress_kind: "navigation",
               progress: %{url: "https://example.com", state: "loaded"},
               progress_seq: 1,
               observed_at: "2026-03-08T13:10:05Z"
             })

    assert {:ok, completed} =
             ExecutionBridge.complete_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               action_id: "action-complete-1",
               normalized_result: %{title: "Example Domain"},
               raw_result_artifact_id: "artifact-browser-result-1",
               completed_at: "2026-03-08T13:10:10Z"
             })

    assert completed.status == "succeeded"

    projection = Runtime.projection(session_id)
    assert projection.in_flight_actions == []

    assert Enum.any?(
             projection.recent_artifacts,
             &(&1.artifact_id == "artifact-browser-result-1")
           )

    assert Enum.any?(Runtime.events(session_id), &(&1.type == "action.progressed"))
    assert Enum.any?(Runtime.events(session_id), &(&1.type == "action.succeeded"))

    artifact_event =
      Runtime.events(session_id)
      |> Enum.find(
        &(&1.type == "artifact.registered" and
            &1.payload.artifact_id == "artifact-browser-result-1")
      )

    assert artifact_event.trace_id == "trace-complete-1"
  end

  test "deduplicates at-least-once progress callbacks by progress sequence", %{
    session_id: session_id
  } do
    execution_id =
      dispatch_action!(session_id, "action-progress-dedupe-1", "trace-progress-dedupe-1")

    session_ref = session_ref(session_id)

    assert {:ok, _accepted} =
             ExecutionBridge.accept_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               worker_id: "worker-browser-dedupe-1",
               accepted_at: "2026-03-08T13:11:00Z"
             })

    progress_payload = %{
      ref: session_ref,
      execution_id: execution_id,
      action_id: "action-progress-dedupe-1",
      progress_kind: "navigation",
      progress: %{url: "https://example.com", state: "loaded"},
      progress_seq: 1,
      observed_at: "2026-03-08T13:11:05Z"
    }

    assert {:ok, _progress} = ExecutionBridge.progress_action("browser", progress_payload)
    assert {:ok, execution} = ExecutionBridge.progress_action("browser", progress_payload)
    assert execution.last_progress_seq == 1

    assert Runtime.events(session_id)
           |> Enum.count(
             &(&1.type == "action.progressed" and &1.payload.execution_id == execution_id)
           ) == 1
  end

  test "propagates failure taxonomy and marks uncertain actions as degraded", %{
    session_id: session_id
  } do
    execution_id = dispatch_action!(session_id, "action-fail-1", "trace-fail-1")
    session_ref = session_ref(session_id)

    assert {:ok, _accepted} =
             ExecutionBridge.accept_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               worker_id: "worker-browser-2",
               accepted_at: "2026-03-08T13:12:00Z"
             })

    assert {:ok, failed} =
             ExecutionBridge.fail_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               action_id: "action-fail-1",
               error_code: "browser_target_detached",
               error_class: "external_dependency",
               retryable: true,
               safe_to_retry: false,
               compensation_possible: false,
               uncertain_side_effect: true,
               details_artifact_id: "artifact-browser-error-1",
               failed_at: "2026-03-08T13:12:05Z"
             })

    assert failed.status == "uncertain"
    assert Runtime.projection(session_id).health == "degraded"

    failed_event =
      Runtime.events(session_id)
      |> Enum.find(&(&1.type == "action.failed"))

    assert failed_event.trace_id == "trace-fail-1"
    assert failed_event.payload.error_code == "browser_target_detached"
    assert failed_event.payload.uncertain_side_effect

    artifact_event =
      Runtime.events(session_id)
      |> Enum.find(
        &(&1.type == "artifact.registered" and
            &1.payload.artifact_id == "artifact-browser-error-1")
      )

    assert artifact_event.trace_id == "trace-fail-1"
  end

  test "publishes cancel commands and records worker cancellation callbacks", %{
    session_id: session_id
  } do
    execution_id = dispatch_action!(session_id, "action-cancel-1", "trace-cancel-1")
    session_ref = session_ref(session_id)

    assert {:ok, _accepted} =
             ExecutionBridge.accept_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               worker_id: "worker-browser-3",
               accepted_at: "2026-03-08T13:14:00Z"
             })

    assert {:ok, ^execution_id} =
             ExecutionBridge.request_action_cancel(
               session_id,
               "action-cancel-1",
               "operator_abort"
             )

    assert [{:ok, cancel_result}] = ExecutionBridge.flush_dispatches()

    cancel_message =
      ExecutionBridge.published_messages()
      |> Enum.find(&(&1.subject == "aegis.v1.command.cancel.browser"))

    assert cancel_message.payload.execution_id == execution_id
    assert cancel_result.execution_id == execution_id

    assert {:ok, cancelled} =
             ExecutionBridge.cancel_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               action_id: "action-cancel-1",
               worker_id: "worker-browser-3",
               reason: "operator_abort",
               cancelled_at: "2026-03-08T13:14:05Z"
             })

    assert cancelled.status == "cancelled"

    refute Enum.any?(
             Runtime.projection(session_id).in_flight_actions,
             &(&1.action_id == "action-cancel-1")
           )

    assert Enum.any?(Runtime.events(session_id), &(&1.type == "action.cancelled"))
  end

  test "marks dispatches failed when the accept deadline expires before worker acceptance", %{
    session_id: session_id
  } do
    execution_id =
      dispatch_action!(session_id, "action-accept-timeout-1", "trace-accept-timeout-1",
        accept_deadline: "2026-03-08T13:15:05Z"
      )

    assert [{:ok, {:accept_timeout, ^execution_id}}] =
             ExecutionBridge.scan_timeouts(~U[2026-03-08 13:15:06Z])

    execution = ExecutionBridge.execution(execution_id)
    assert execution.status == "failed"
    assert execution.failure_error_code == "accept_deadline_exceeded"
    assert execution.failure_error_class == "transport_timeout"

    failed_event =
      Runtime.events(session_id)
      |> Enum.find(&(&1.type == "action.failed" and &1.payload.execution_id == execution_id))

    assert failed_event.trace_id == "trace-accept-timeout-1"
    assert failed_event.payload.error_code == "accept_deadline_exceeded"
  end

  test "marks accepted executions uncertain when the hard deadline expires", %{
    session_id: session_id
  } do
    execution_id =
      dispatch_action!(session_id, "action-hard-timeout-1", "trace-hard-timeout-1",
        hard_deadline: "2026-03-08T13:17:03Z"
      )

    session_ref = session_ref(session_id)

    assert {:ok, _accepted} =
             ExecutionBridge.accept_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               worker_id: "worker-browser-hard-timeout-1",
               accepted_at: "2026-03-08T13:17:00Z"
             })

    assert {:ok, _heartbeat} =
             ExecutionBridge.action_heartbeat("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               action_id: "action-hard-timeout-1",
               worker_id: "worker-browser-hard-timeout-1",
               heartbeat_seq: 1,
               observed_at: "2026-03-08T13:17:01Z"
             })

    assert [{:ok, {:hard_timeout, ^execution_id}}] =
             ExecutionBridge.scan_timeouts(~U[2026-03-08 13:17:04Z])

    execution = ExecutionBridge.execution(execution_id)
    assert execution.status == "uncertain"
    assert execution.failure_error_code == "hard_deadline_exceeded"
    assert execution.failure_error_class == "execution_timeout"

    failed_event =
      Runtime.events(session_id)
      |> Enum.find(&(&1.type == "action.failed" and &1.payload.execution_id == execution_id))

    assert failed_event.trace_id == "trace-hard-timeout-1"
    assert failed_event.payload.uncertain_side_effect
    assert Runtime.projection(session_id).health == "degraded"
  end

  test "detects missed heartbeats and emits worker-loss events", %{session_id: session_id} do
    execution_id =
      dispatch_action!(session_id, "action-lost-1", "trace-lost-1",
        hard_deadline: "2026-03-08T13:16:40Z"
      )

    session_ref = session_ref(session_id)

    assert {:ok, _accepted} =
             ExecutionBridge.accept_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               worker_id: "worker-browser-4",
               accepted_at: "2026-03-08T13:16:00Z"
             })

    assert [{:ok, {:worker_lost, ^execution_id}}] =
             ExecutionBridge.scan_timeouts(~U[2026-03-08 13:16:20Z])

    execution = ExecutionBridge.execution(execution_id)
    assert execution.status == "lost"

    assert Enum.any?(Runtime.events(session_id), &(&1.type == "action.heartbeat_missed"))
    assert Enum.any?(Runtime.events(session_id), &(&1.type == "system.worker_lost"))
    assert Runtime.projection(session_id).health == "degraded"
  end

  test "nacks and exhausts redelivery when worker callbacks target unknown executions", %{
    session_id: session_id
  } do
    session_ref = session_ref(session_id)

    assert {:error, :unknown_execution} =
             ExecutionBridge.progress_action("browser", %{
               ref: session_ref,
               execution_id: "missing-execution",
               action_id: "missing-action",
               progress_kind: "navigation",
               progress: %{url: "https://example.com"},
               progress_seq: 1,
               observed_at: "2026-03-08T13:18:05Z"
             })

    published = List.last(ExecutionBridge.published_messages())
    assert published.subject == "aegis.v1.event.progress.browser"
    assert published.ack_status == :max_deliver_exceeded
    assert length(published.deliveries) == 10
    assert Enum.all?(published.deliveries, &(&1.status == :nack))
  end

  test "guardrails permit only execution-bridge-owned tables" do
    assert :ok = Guardrails.assert_write_allowed!("action_executions")
    assert :ok = Guardrails.assert_write_allowed!("worker_registrations")

    assert_raise ArgumentError, ~r/canonical table "session_events"/, fn ->
      Guardrails.assert_write_allowed!("session_events")
    end

    assert_raise ArgumentError, ~r/canonical table "outbox"/, fn ->
      Guardrails.assert_write_allowed!("outbox")
    end

    assert_raise ArgumentError, ~r/canonical table "approvals"/, fn ->
      Guardrails.assert_write_allowed!("approvals")
    end
  end

  defp dispatch_action!(session_id, action_id, trace_id, action_overrides \\ %{}) do
    {:ok, lease} = Runtime.lease(session_id)

    action =
      Map.merge(
        %{
          action_id: action_id,
          tool_id: "browser.navigate",
          tool_schema_version: "v1",
          worker_kind: "browser",
          input: %{url: "https://example.com"},
          risk_class: "read_only",
          idempotency_class: "idempotent",
          timeout_class: "short",
          mutating: false
        },
        Map.new(action_overrides)
      )

    assert {:ok, _result} =
             Runtime.dispatch(
               session_id,
               {:request_action, action},
               owner_node: lease.owner_node,
               lease_epoch: lease.lease_epoch,
               trace_id: trace_id,
               idempotency_key: "idem-#{action_id}"
             )

    assert [{:ok, %{execution_id: execution_id}}] = ExecutionBridge.flush_dispatches()
    execution_id
  end

  defp session_ref(session_id) do
    {:ok, replay} = Runtime.historical_replay(session_id)

    %{
      tenant_id: replay.replay_state.tenant_id,
      workspace_id: replay.replay_state.workspace_id,
      session_id: replay.replay_state.session_id,
      lease_epoch: replay.replay_state.lease_epoch
    }
  end
end
