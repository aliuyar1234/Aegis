defmodule Aegis.ExecutionBridge.AdmissionControlTest do
  use ExUnit.Case, async: false

  alias Aegis.Events
  alias Aegis.ExecutionBridge
  alias Aegis.Runtime

  setup do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(Aegis.Repo)
    Ecto.Adapters.SQL.Sandbox.mode(Aegis.Repo, {:shared, self()})

    Events.reset!()
    ExecutionBridge.reset!()

    original_limits = Application.get_env(:aegis_policy, :quota_limits)

    on_exit(fn ->
      if is_nil(original_limits) do
        Application.delete_env(:aegis_policy, :quota_limits)
      else
        Application.put_env(:aegis_policy, :quota_limits, original_limits)
      end
    end)

    :ok
  end

  test "rejects new live sessions when the scoped session quota is exhausted" do
    put_quota_limits(%{
      tier_a: %{
        live_sessions: 1,
        concurrent_browser_contexts: 4,
        concurrent_effectful_actions: 2
      }
    })

    session_attrs = %{
      session_id: unique_session_id("quota-live"),
      tenant_id: "tenant-admission",
      workspace_id: "workspace-admission",
      requested_by: "security-suite",
      session_kind: "browser_operation"
    }

    {:ok, first_tree_pid} = Runtime.start_session(session_attrs)

    on_exit(fn ->
      if Process.alive?(first_tree_pid) do
        Process.exit(first_tree_pid, :shutdown)
      end
    end)

    assert {:error,
            {:quota_exceeded, :live_sessions,
             %{
               limit: 1,
               current: 1,
               tenant_id: "tenant-admission",
               workspace_id: "workspace-admission",
               isolation_tier: "tier_a"
             }}} =
             Runtime.start_session(%{session_attrs | session_id: unique_session_id("quota-blocked")})

    assert :ok =
             DynamicSupervisor.terminate_child(Aegis.Runtime.SessionHostSupervisor, first_tree_pid)

    wait_for_exit!(first_tree_pid)

    assert {:ok, restarted_tree_pid} = Runtime.start_session(session_attrs)

    on_exit(fn ->
      if Process.alive?(restarted_tree_pid) do
        Process.exit(restarted_tree_pid, :shutdown)
      end
    end)
  end

  test "defers browser dispatch until a browser context slot becomes available" do
    put_quota_limits(%{
      tier_a: %{
        live_sessions: 10,
        concurrent_browser_contexts: 1,
        concurrent_effectful_actions: 4
      }
    })

    session_one = start_active_session!("browser-one")
    session_two = start_active_session!("browser-two")

    request_action!(session_one, "action-browser-1", "browser.navigate", %{url: "https://example.com"})
    request_action!(session_two, "action-browser-2", "browser.navigate", %{url: "https://example.com"})

    assert [
             {:ok, %{execution_id: execution_id}},
             {:ok,
              %{
                deferred: true,
                action_id: "action-browser-2",
                quota_class: :concurrent_browser_contexts,
                quota: %{limit: 1, current: 1}
              }}
           ] = ExecutionBridge.flush_dispatches()

    assert dispatch_message_count() == 1

    finish_execution!(session_one, execution_id, "action-browser-1")

    assert [{:ok, %{execution_id: second_execution_id}}] = ExecutionBridge.flush_dispatches()
    assert is_binary(second_execution_id)
    assert dispatch_message_count() == 2
  end

  test "defers effectful dispatch until an effectful action slot becomes available" do
    put_quota_limits(%{
      tier_a: %{
        live_sessions: 10,
        concurrent_browser_contexts: 4,
        concurrent_effectful_actions: 1
      }
    })

    session_one = start_active_session!("effectful-one")
    session_two = start_active_session!("effectful-two")

    request_action!(session_one, "action-effect-1", "browser.click", %{selector: "#save"})
    request_action!(session_two, "action-effect-2", "browser.click", %{selector: "#save"})

    assert [
             {:ok, %{execution_id: execution_id}},
             {:ok,
              %{
                deferred: true,
                action_id: "action-effect-2",
                quota_class: :concurrent_effectful_actions,
                quota: %{limit: 1, current: 1}
              }}
           ] = ExecutionBridge.flush_dispatches()

    assert dispatch_message_count() == 1

    finish_execution!(session_one, execution_id, "action-effect-1")

    assert [{:ok, %{execution_id: second_execution_id}}] = ExecutionBridge.flush_dispatches()
    assert is_binary(second_execution_id)
    assert dispatch_message_count() == 2
  end

  defp put_quota_limits(limits) do
    Application.put_env(:aegis_policy, :quota_limits, limits)
  end

  defp start_active_session!(prefix) do
    session_id = unique_session_id(prefix)

    {:ok, tree_pid} =
      Runtime.start_session(%{
        session_id: session_id,
        tenant_id: "tenant-admission",
        workspace_id: "workspace-admission",
        requested_by: "security-suite",
        session_kind: "browser_operation"
      })

    on_exit(fn ->
      if Process.alive?(tree_pid) do
        Process.exit(tree_pid, :shutdown)
      end
    end)

    {:ok, lease} = Runtime.lease(session_id)

    assert {:ok, _result} =
             Runtime.dispatch(
               session_id,
               {:activate, %{owner_node: lease.owner_node, lease_epoch: lease.lease_epoch}},
               owner_node: lease.owner_node,
               lease_epoch: lease.lease_epoch
             )

    session_id
  end

  defp request_action!(session_id, action_id, tool_id, input) do
    {:ok, lease} = Runtime.lease(session_id)

    assert {:ok, _result} =
             Runtime.dispatch(
               session_id,
               {:request_action,
                %{
                  action_id: action_id,
                  tool_id: tool_id,
                  tool_schema_version: "v1",
                  worker_kind: "browser",
                  input: input
                }},
               owner_node: lease.owner_node,
               lease_epoch: lease.lease_epoch,
               trace_id: "trace-#{action_id}",
               idempotency_key: "idem-#{action_id}"
             )
  end

  defp finish_execution!(session_id, execution_id, action_id) do
    session_ref = session_ref(session_id)

    assert {:ok, _accepted} =
             ExecutionBridge.accept_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               worker_id: "worker-browser-admission",
               accepted_at: "2026-03-08T15:00:00Z"
             })

    assert {:ok, _completed} =
             ExecutionBridge.complete_action("browser", %{
               ref: session_ref,
               execution_id: execution_id,
               action_id: action_id,
               normalized_result: %{status: "ok"},
               raw_result_artifact_id: "artifact-#{action_id}",
               completed_at: "2026-03-08T15:00:05Z"
             })
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

  defp unique_session_id(prefix) do
    "#{prefix}-#{System.unique_integer([:positive])}"
  end

  defp dispatch_message_count do
    ExecutionBridge.published_messages()
    |> Enum.count(&String.starts_with?(&1.subject, "aegis.v1.command.dispatch."))
  end

  defp wait_for_exit!(pid, attempts \\ 20)

  defp wait_for_exit!(pid, attempts) when attempts > 0 do
    if Process.alive?(pid) do
      Process.sleep(50)
      wait_for_exit!(pid, attempts - 1)
    else
      :ok
    end
  end

  defp wait_for_exit!(pid, 0) do
    refute Process.alive?(pid)
  end
end
