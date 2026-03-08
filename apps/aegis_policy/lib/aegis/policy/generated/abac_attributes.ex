defmodule Aegis.Policy.Generated.AbacAttributes do
  @moduledoc false

  @source_digest "973eb741435ccf0ffc7a33685ba19273c797c5ec7984fab278ab6dc97d080111"
  @source_files ["meta/abac-attributes.yaml"]
  @attributes [
    %{"id" => "tenant_id", "applies_to" => ["session", "artifact", "approval", "operator_request"]},
    %{
      "id" => "workspace_id",
      "applies_to" => ["session", "artifact", "approval", "operator_request"]
    },
    %{"id" => "risk_class", "applies_to" => ["action", "approval"]},
    %{"id" => "data_sensitivity", "applies_to" => ["artifact", "raw_output", "operator_note"]},
    %{"id" => "control_mode", "applies_to" => ["session"]},
    %{"id" => "isolation_tier", "applies_to" => ["tenant", "worker_pool"]},
    %{"id" => "environment", "applies_to" => ["operator_request", "worker_dispatch"]},
    %{"id" => "dangerous_action_class", "applies_to" => ["action", "policy_evaluation"]}
  ]
  @by_id Map.new(@attributes, &{Map.fetch!(&1, "id"), &1})

  def source_digest, do: @source_digest
  def source_files, do: @source_files
  def attributes, do: @attributes
  def by_id, do: @by_id
end
