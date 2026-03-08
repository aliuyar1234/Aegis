defmodule Aegis.Policy.Generated.DangerousActionCatalog do
  @moduledoc false

  @source_digest "cbef9b312876b6a1a9ab616d799623db9f92a9625c2deff2461241f37df42a7d"
  @source_files ["meta/dangerous-action-classes.yaml"]
  @dangerous_action_classes [%{"id" => "browser_write_high", "description" => "High-risk browser mutation with privilege, entitlement, or destructive impact.", "default_decision" => "deny_without_explicit_policy"}, %{"id" => "browser_write_low", "description" => "Low-risk browser mutation with reversible customer-neutral effect.", "default_decision" => "allow_with_constraints"}, %{"id" => "browser_write_medium", "description" => "Browser mutation affecting customer-visible state with bounded blast radius.", "default_decision" => "require_approval"}, %{"id" => "destructive", "description" => "Deletion, revocation, or irreversible mutation.", "default_decision" => "require_approval"}, %{"id" => "external_message", "description" => "Outbound communication triggered by the runtime.", "default_decision" => "require_approval"}, %{"id" => "financial", "description" => "Financial or billing mutation.", "default_decision" => "require_approval"}, %{"id" => "pii_export", "description" => "Export or reveal sensitive customer data.", "default_decision" => "deny_without_explicit_policy"}]
  @by_id Map.new(@dangerous_action_classes, &{Map.fetch!(&1, "id"), &1})

  def source_digest, do: @source_digest
  def source_files, do: @source_files
  def dangerous_action_classes, do: @dangerous_action_classes
  def by_id, do: @by_id
end
