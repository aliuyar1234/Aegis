defmodule Aegis.Policy.AuthorizerTest do
  use ExUnit.Case, async: true

  alias Aegis.Policy.Authorizer

  test "scopes operator fleet access to tenant and workspace" do
    auth = %{
      actor_id: "operator-1",
      role: "operator",
      tenant_id: "tenant-ops",
      workspace_id: "workspace-ops",
      environment: "production"
    }

    assert {:ok, scoped_filters} = Authorizer.scope_filters(auth, "session-fleet", %{})
    assert scoped_filters.tenant_id == "tenant-ops"
    assert scoped_filters.workspace_id == "workspace-ops"

    assert {:ok, _decision} =
             Authorizer.authorize_surface(
               auth,
               "session-detail",
               %{tenant_id: "tenant-ops", workspace_id: "workspace-ops"}
             )
  end

  test "denies replay to operators and allows it for auditors" do
    operator = %{
      actor_id: "operator-1",
      role: "operator",
      tenant_id: "tenant-ops",
      workspace_id: "workspace-ops",
      environment: "production"
    }

    auditor = %{
      actor_id: "auditor-1",
      role: "auditor",
      tenant_id: "tenant-ops",
      workspace_id: "workspace-ops",
      environment: "production"
    }

    assert {:error, {:forbidden, :surface_not_allowed}} =
             Authorizer.authorize_surface(operator, "replay", %{
               tenant_id: "tenant-ops",
               workspace_id: "workspace-ops"
             })

    assert {:ok, _decision} =
             Authorizer.authorize_surface(auditor, "replay", %{
               tenant_id: "tenant-ops",
               workspace_id: "workspace-ops"
             })
  end

  test "allows developer detail access only outside production" do
    prod_developer = %{
      actor_id: "developer-1",
      role: "developer",
      tenant_id: "tenant-dev",
      workspace_id: "workspace-dev",
      environment: "production"
    }

    nonprod_developer = %{prod_developer | environment: "staging"}

    assert {:error, {:forbidden, :surface_not_allowed}} =
             Authorizer.authorize_surface(prod_developer, "session-detail", %{
               tenant_id: "tenant-dev",
               workspace_id: "workspace-dev"
             })

    assert {:ok, _decision} =
             Authorizer.authorize_surface(nonprod_developer, "session-detail", %{
               tenant_id: "tenant-dev",
               workspace_id: "workspace-dev"
             })
  end

  test "enforces approval dangerous-action classes by role" do
    operator = %{
      actor_id: "operator-1",
      role: "operator",
      tenant_id: "tenant-ops",
      workspace_id: "workspace-ops",
      environment: "production"
    }

    reviewer = %{
      actor_id: "reviewer-1",
      role: "reviewer",
      tenant_id: "tenant-ops",
      workspace_id: "workspace-ops",
      environment: "production"
    }

    approval = %{
      tenant_id: "tenant-ops",
      workspace_id: "workspace-ops",
      dangerous_action_class: "destructive"
    }

    assert {:error, {:forbidden, :approval_class_not_allowed}} =
             Authorizer.authorize_approval_action(operator, "grant_approval", approval)

    assert {:ok, _decision} =
             Authorizer.authorize_approval_action(reviewer, "grant_approval", approval)
  end

  test "allows platform admin to cross tenant scope" do
    admin = %{
      actor_id: "platform-admin-1",
      role: "platform_admin",
      environment: "production",
      reveal_redacted: true
    }

    assert {:ok, decision} =
             Authorizer.authorize_surface(admin, "replay", %{
               tenant_id: "tenant-other",
               workspace_id: "workspace-other"
             })

    assert decision.can_reveal_redacted
  end
end
