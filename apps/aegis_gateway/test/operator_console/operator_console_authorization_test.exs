defmodule OperatorConsoleAuthorizationTest do
  use ExUnit.Case, async: false

  alias Aegis.Events
  alias Aegis.ExecutionBridge
  alias Aegis.Gateway.OperatorConsole
  alias Aegis.Runtime

  setup do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(Aegis.Repo)
    Ecto.Adapters.SQL.Sandbox.mode(Aegis.Repo, {:shared, self()})

    Events.reset!()
    ExecutionBridge.reset!()

    :ok
  end

  test "scopes fleet and detail access by tenant and workspace" do
    visible_session =
      start_session!(%{
        session_id: unique_session_id("visible"),
        tenant_id: "tenant-ops",
        workspace_id: "workspace-ops"
      })

    hidden_session =
      start_session!(%{
        session_id: unique_session_id("hidden"),
        tenant_id: "tenant-other",
        workspace_id: "workspace-other"
      })

    activate!(visible_session)
    activate!(hidden_session)

    auth = operator_auth("tenant-ops", "workspace-ops")

    assert {:ok, fleet} = OperatorConsole.session_fleet(auth)
    assert Enum.map(fleet.sessions, & &1.session_id) == [visible_session]

    assert {:ok, _detail} = OperatorConsole.session_detail(auth, visible_session)
    assert {:error, :unknown_session} = OperatorConsole.session_detail(auth, hidden_session)
  end

  test "enforces replay and developer read access by role and environment" do
    session_id =
      start_session!(%{
        session_id: unique_session_id("replay-auth"),
        tenant_id: "tenant-auth",
        workspace_id: "workspace-auth"
      })

    activate!(session_id)

    operator = operator_auth("tenant-auth", "workspace-auth")
    reviewer = reviewer_auth("tenant-auth", "workspace-auth")
    developer = developer_auth("tenant-auth", "workspace-auth")

    assert {:error, {:forbidden, :surface_not_allowed}} =
             OperatorConsole.session_replay(operator, session_id)

    assert {:ok, _replay} = OperatorConsole.session_replay(reviewer, session_id)

    assert {:ok, detail} = OperatorConsole.session_detail(developer, session_id)
    refute detail.controls.pause
    refute detail.controls.abort
    refute detail.controls.take_control
  end

  test "rejects unauthorized operator mutations and approval resolutions" do
    session_id =
      start_session!(%{
        session_id: unique_session_id("approval-auth"),
        tenant_id: "tenant-approval-auth",
        workspace_id: "workspace-approval-auth"
      })

    activate!(session_id)
    request_destructive_submit_action!(session_id, "action-destructive-1")

    operator = operator_auth("tenant-approval-auth", "workspace-approval-auth")
    reviewer = reviewer_auth("tenant-approval-auth", "workspace-approval-auth")
    auditor = auditor_auth("tenant-approval-auth", "workspace-approval-auth")

    assert {:error, {:forbidden, :surface_not_allowed}} =
             OperatorConsole.pause_session(auditor, session_id, "manual_review")

    assert {:ok, detail} = OperatorConsole.session_detail(operator, session_id)
    [%{approval_id: approval_id, action_hash: action_hash}] = detail.approvals

    assert {:error, {:forbidden, :approval_class_not_allowed}} =
             OperatorConsole.grant_approval(operator, session_id, approval_id, action_hash)

    assert {:ok, _result} =
             OperatorConsole.grant_approval(reviewer, session_id, approval_id, action_hash)

    assert {:ok, updated_detail} = OperatorConsole.session_detail(operator, session_id)
    assert updated_detail.approvals == []
  end

  defp start_session!(attrs) do
    session_id = Map.fetch!(attrs, :session_id)

    {:ok, tree_pid} =
      Runtime.start_session(
        Map.merge(
          %{
            requested_by: "operator-console-auth-test",
            session_kind: "browser_operation"
          },
          attrs
        )
      )

    on_exit(fn ->
      if Process.alive?(tree_pid) do
        Process.exit(tree_pid, :shutdown)
      end
    end)

    session_id
  end

  defp activate!(session_id) do
    {:ok, lease} = Runtime.lease(session_id)

    assert {:ok, _result} =
             Runtime.dispatch(
               session_id,
               {:activate, %{owner_node: lease.owner_node, lease_epoch: lease.lease_epoch}},
               owner_node: lease.owner_node,
               lease_epoch: lease.lease_epoch
             )
  end

  defp request_destructive_submit_action!(session_id, action_id) do
    {:ok, lease} = Runtime.lease(session_id)

    assert {:ok, _result} =
             Runtime.dispatch(
               session_id,
               {:request_action,
                %{
                  action_id: action_id,
                  tool_id: "browser.submit",
                  tool_schema_version: "v1",
                  worker_kind: "browser",
                  input: %{selector: "form#danger"},
                  dangerous_action_class: "destructive"
                }},
               owner_node: lease.owner_node,
               lease_epoch: lease.lease_epoch
             )
  end

  defp operator_auth(tenant_id, workspace_id, overrides \\ %{}) do
    overrides = Map.new(overrides)

    Map.merge(
      %{
        actor_id: "operator-auth-1",
        role: "operator",
        tenant_id: tenant_id,
        workspace_id: workspace_id,
        environment: "production",
        reveal_redacted: false
      },
      overrides
    )
  end

  defp reviewer_auth(tenant_id, workspace_id, overrides \\ %{}) do
    overrides = Map.new(overrides)

    Map.merge(
      %{
        actor_id: "reviewer-auth-1",
        role: "reviewer",
        tenant_id: tenant_id,
        workspace_id: workspace_id,
        environment: "production",
        reveal_redacted: false
      },
      overrides
    )
  end

  defp auditor_auth(tenant_id, workspace_id, overrides \\ %{}) do
    overrides = Map.new(overrides)

    Map.merge(
      %{
        actor_id: "auditor-auth-1",
        role: "auditor",
        tenant_id: tenant_id,
        workspace_id: workspace_id,
        environment: "production",
        reveal_redacted: false
      },
      overrides
    )
  end

  defp developer_auth(tenant_id, workspace_id) do
    developer_auth(tenant_id, workspace_id, %{})
  end

  defp developer_auth(tenant_id, workspace_id, overrides) do
    overrides = Map.new(overrides)

    Map.merge(
      %{
        actor_id: "developer-auth-1",
        role: "developer",
        tenant_id: tenant_id,
        workspace_id: workspace_id,
        environment: "staging",
        reveal_redacted: false
      },
      overrides
    )
  end

  defp unique_session_id(prefix) do
    "#{prefix}-#{System.unique_integer([:positive])}"
  end
end
