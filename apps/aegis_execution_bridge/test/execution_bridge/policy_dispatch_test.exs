defmodule Aegis.ExecutionBridge.PolicyDispatchTest do
  use ExUnit.Case, async: false

  alias Aegis.Events
  alias Aegis.ExecutionBridge
  alias Aegis.Runtime

  setup do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(Aegis.Repo)
    Ecto.Adapters.SQL.Sandbox.mode(Aegis.Repo, {:shared, self()})

    Events.reset!()
    ExecutionBridge.reset!()

    session_id = "policy-session-#{System.unique_integer([:positive])}"

    {:ok, tree_pid} =
      Runtime.start_session(%{
        session_id: session_id,
        tenant_id: "tenant-policy",
        workspace_id: "workspace-policy",
        requested_by: "policy-suite",
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

  test "dispatches read actions only after policy.evaluated allow", %{session_id: session_id} do
    request_action!(session_id, "action-read-1", "browser.navigate", %{url: "https://example.com"})

    assert [{:ok, dispatch_result}] = ExecutionBridge.flush_dispatches()

    [published] = ExecutionBridge.published_messages()
    assert published.subject == "aegis.v1.command.dispatch.browser"
    assert published.payload.action_id == "action-read-1"
    assert published.payload.capability_token == ""
    assert dispatch_result.execution_id

    policy_event =
      Runtime.events(session_id)
      |> Enum.find(&(&1.type == "policy.evaluated"))

    assert policy_event.payload.decision == "allow"

    outbox_row =
      Events.outbox(session_id)
      |> Enum.find(&(&1.event_type == "policy.evaluated"))

    assert outbox_row.status == "published"
  end

  test "issues capability tokens for allow-with-constraints browser writes before dispatch", %{
    session_id: session_id
  } do
    request_action!(session_id, "action-click-1", "browser.click", %{selector: "#save"})

    assert [{:ok, _dispatch_result}] = ExecutionBridge.flush_dispatches()

    [published] = ExecutionBridge.published_messages()
    assert published.payload.action_id == "action-click-1"
    assert published.payload.capability_token != ""

    claims = decode_token!(published.payload.capability_token)
    assert claims["action_id"] == "action-click-1"
    assert claims["tool_id"] == "browser.click"
    assert claims["dangerous_action_class"] == "browser_write_low"
    assert claims["issued_to_worker_kind"] == "browser"

    action =
      Runtime.snapshot(session_id).durable.action_ledger
      |> Enum.find(&(&1.action_id == "action-click-1"))

    assert action.approved_argument_digest == claims["approved_argument_digest"]
  end

  test "holds medium-risk browser writes until approval is granted", %{session_id: session_id} do
    request_action!(session_id, "action-submit-1", "browser.submit", %{selector: "form#profile"})

    assert [{:ok, %{skipped: true, action_id: "action-submit-1"}}] =
             ExecutionBridge.flush_dispatches()

    assert ExecutionBridge.published_messages() == []
    projection = Runtime.projection(session_id)
    assert projection.wait_reason == "approval"
    assert [%{approval_id: approval_id, action_hash: action_hash}] = projection.pending_approvals

    dispatch_runtime!(
      session_id,
      {:grant_approval,
       %{
         approval_id: approval_id,
         action_hash: action_hash,
         decided_by: "operator-1"
       }}
    )

    assert Runtime.projection(session_id).pending_approvals == []
    assert Runtime.projection(session_id).phase == "active"

    assert [{:ok, dispatch_result}] = ExecutionBridge.flush_dispatches()

    [published] = ExecutionBridge.published_messages()
    assert published.payload.action_id == "action-submit-1"
    assert published.payload.capability_token != ""
    assert dispatch_result.execution_id

    event_types = Runtime.events(session_id) |> Enum.map(& &1.type)

    assert "approval.requested" in event_types
    assert "approval.granted" in event_types
    assert "action.dispatched" in event_types
  end

  test "marks approval-bound writes expired without dispatching them", %{session_id: session_id} do
    request_action!(session_id, "action-expire-1", "browser.submit", %{selector: "form#danger"})

    assert [{:ok, %{skipped: true, action_id: "action-expire-1"}}] =
             ExecutionBridge.flush_dispatches()

    [%{approval_id: approval_id, action_hash: action_hash}] = Runtime.projection(session_id).pending_approvals

    dispatch_runtime!(
      session_id,
      {:expire_approval,
       %{
         approval_id: approval_id,
         action_hash: action_hash,
         expired_at: "2026-03-08T13:30:00Z"
       }}
    )

    assert ExecutionBridge.flush_dispatches() == []
    assert ExecutionBridge.published_messages() == []
    assert Runtime.projection(session_id).pending_approvals == []

    action =
      Runtime.snapshot(session_id).durable.action_ledger
      |> Enum.find(&(&1.action_id == "action-expire-1"))

    assert action.status == "approval_expired"
  end

  test "denies high-risk browser writes before dispatch", %{session_id: session_id} do
    request_action!(session_id, "action-delete-1", "browser.delete", %{selector: "button.delete"})

    assert [{:ok, %{skipped: true, action_id: "action-delete-1"}}] =
             ExecutionBridge.flush_dispatches()

    assert ExecutionBridge.published_messages() == []
    assert Runtime.projection(session_id).in_flight_actions == []

    action =
      Runtime.snapshot(session_id).durable.action_ledger
      |> Enum.find(&(&1.action_id == "action-delete-1"))

    assert action.status == "denied"
    assert action.policy_decision == "deny"
  end

  defp request_action!(session_id, action_id, tool_id, input) do
    dispatch_runtime!(
      session_id,
      {:request_action,
       %{
         action_id: action_id,
         tool_id: tool_id,
         tool_schema_version: "v1",
         worker_kind: "browser",
         input: input
       }}
    )
  end

  defp dispatch_runtime!(session_id, command) do
    {:ok, lease} = Runtime.lease(session_id)

    assert {:ok, _result} =
             Runtime.dispatch(
               session_id,
               command,
               owner_node: lease.owner_node,
               lease_epoch: lease.lease_epoch
             )
  end

  defp decode_token!(token) do
    <<"aegis.ctk.v1.", encoded::binary>> = token
    {:ok, raw} = Base.url_decode64(encoded, padding: false)
    :erlang.binary_to_term(raw)
  end
end
