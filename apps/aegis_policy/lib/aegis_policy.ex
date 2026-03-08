defmodule AegisPolicy do
  @moduledoc """
  Boundary module for tool policy, approvals, and capability issuance.

  The Phase 01 runtime owns action requests, not the policy truth that evaluates
  them.
  """

  defdelegate tool_descriptors(), to: Aegis.Policy.ToolRegistry, as: :all
  defdelegate tool_descriptor(tool_id), to: Aegis.Policy.ToolRegistry, as: :fetch
  defdelegate tool_descriptor!(tool_id), to: Aegis.Policy.ToolRegistry, as: :fetch!
  defdelegate tool_ids(), to: Aegis.Policy.ToolRegistry

  defdelegate tool_descriptors_for_executor(executor_kind),
    to: Aegis.Policy.ToolRegistry,
    as: :by_executor

  defdelegate tool_registry_source_digest(), to: Aegis.Policy.ToolRegistry, as: :source_digest
  defdelegate dangerous_action_classes(), to: Aegis.Policy.DangerousActionCatalog, as: :all
  defdelegate dangerous_action_class(class_id), to: Aegis.Policy.DangerousActionCatalog, as: :fetch
  defdelegate rbac_roles(), to: Aegis.Policy.RbacRoles, as: :all
  defdelegate abac_attributes(), to: Aegis.Policy.AbacAttributes, as: :all
  defdelegate authorize_surface(auth_context, surface, resource \\ %{}),
    to: Aegis.Policy.Authorizer

  defdelegate authorize_operator_action(auth_context, action, resource),
    to: Aegis.Policy.Authorizer

  defdelegate authorize_approval_action(auth_context, action, approval),
    to: Aegis.Policy.Authorizer

  defdelegate scope_filters(auth_context, surface, filters \\ %{}), to: Aegis.Policy.Authorizer
  defdelegate filter_allowed_workspaces(resources, auth_context), to: Aegis.Policy.Authorizer
  defdelegate redact_controls(controls, auth_context), to: Aegis.Policy.Authorizer
  defdelegate allow_approval_controls?(auth_context, approvals), to: Aegis.Policy.Authorizer
  defdelegate evaluate_action(request, session_context), to: Aegis.Policy.Evaluator
  defdelegate build_approval_request(session_context, action, decision, metadata),
    to: Aegis.Policy.Evaluator
  defdelegate quota_limit(quota_class, attrs), to: Aegis.Policy.QuotaPolicy, as: :limit_for
  defdelegate isolation_tier(attrs), to: Aegis.Policy.QuotaPolicy

  defdelegate issue_capability_token(session_context, action, opts \\ %{}),
    to: Aegis.Policy.Evaluator

  defdelegate approval_expires_at(request), to: Aegis.Policy.Evaluator
  defdelegate decode_capability_token(token), to: Aegis.Policy.CapabilityToken, as: :decode
  defdelegate digest_claims(value), to: Aegis.Policy.Evaluator, as: :digest
end
