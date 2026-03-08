defmodule Aegis.Policy.Generated.RbacRoles do
  @moduledoc false

  @source_digest "308435b9380c0adec102f4fe7485fa09f918da3527da86d740e5d4e18b118d30"
  @source_files ["meta/rbac-roles.yaml"]
  @roles [
    %{
      "id" => "platform_admin",
      "description" => "Global control-plane admin for deployment and tenancy operations.",
      "allowed_surfaces" => ["operator-console-admin", "api-admin"],
      "can_approve" => ["all"],
      "can_reveal_redacted" => true
    },
    %{
      "id" => "operator",
      "description" => "Handles routine session supervision and intervention.",
      "allowed_surfaces" => ["session-fleet", "session-detail", "approvals-queue"],
      "can_approve" => ["browser_write_low", "browser_write_medium"],
      "can_reveal_redacted" => false
    },
    %{
      "id" => "reviewer",
      "description" => "Approves risky writes and audits evidence.",
      "allowed_surfaces" => ["approvals-queue", "replay"],
      "can_approve" => ["browser_write_high", "financial", "destructive"],
      "can_reveal_redacted" => false
    },
    %{
      "id" => "auditor",
      "description" => "Read-only access to replay, audit exports, and runbooks.",
      "allowed_surfaces" => ["replay", "audit-export"],
      "can_approve" => [],
      "can_reveal_redacted" => false
    },
    %{
      "id" => "developer",
      "description" =>
        "Implements runtime code and may inspect non-restricted metadata in non-production workspaces.",
      "allowed_surfaces" => ["dev-session-detail"],
      "can_approve" => [],
      "can_reveal_redacted" => false
    }
  ]
  @by_id Map.new(@roles, &{Map.fetch!(&1, "id"), &1})

  def source_digest, do: @source_digest
  def source_files, do: @source_files
  def roles, do: @roles
  def by_id, do: @by_id
end
