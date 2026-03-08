defmodule Aegis.Policy.Evaluator do
  @moduledoc """
  Phase 07 policy evaluator for tool requests, approvals, and capability tokens.

  Source of truth:
  - phase doc: `docs/exec-plans/active/PHASE-07-policy-approvals.md`
  - ADRs: `docs/adr/0009-browser-ops-first-wedge.md`,
    `docs/adr/0011-policy-approval-boundary.md`
  - acceptance: `AC-029`, `AC-030`, `AC-031`, `AC-032`
  - tests: `TS-009`, `TS-011`
  """

  alias Aegis.Policy.{CapabilityToken, DangerousActionCatalog, ToolRegistry}

  @approval_ttl_seconds 900
  @effectful_risk_classes MapSet.new(["browser_write", "write", "destructive", "financial", "external_message"])
  @constrained_control_modes MapSet.new(["supervised", "human_control", "paused"])

  @spec evaluate_action(map(), map()) :: {:ok, map()} | {:error, term()}
  def evaluate_action(request, session_context) when is_map(request) and is_map(session_context) do
    descriptor = ToolRegistry.fetch!(Map.fetch!(request, :tool_id))
    isolation_tier = Map.get(session_context, :isolation_tier, "tier_a") |> normalize_string()
    mutating = mutating?(request, descriptor)
    dangerous_action_class = dangerous_action_class(request, descriptor, mutating)
    risk_class = Map.get(request, :risk_class, descriptor["risk_class"])
    worker_kind = Map.get(request, :worker_kind, derive_worker_kind(Map.fetch!(request, :tool_id)))
    routing = routing_metadata(session_context, worker_kind, isolation_tier)
    decision = decide(session_context, mutating, dangerous_action_class)
    input_digest = digest(Map.get(request, :input, %{}))

    action_core =
      %{
        tenant_id: Map.fetch!(session_context, :tenant_id),
        workspace_id: Map.fetch!(session_context, :workspace_id),
        isolation_tier: isolation_tier,
        session_id: Map.fetch!(session_context, :session_id),
        action_id: Map.fetch!(request, :action_id),
        tool_id: Map.fetch!(request, :tool_id),
        tool_schema_version: Map.get(request, :tool_schema_version, descriptor["version"]),
        worker_kind: worker_kind,
        worker_pool_id: routing.worker_pool_id,
        dispatch_route_key: routing.dispatch_route_key,
        risk_class: risk_class,
        dangerous_action_class: dangerous_action_class,
        idempotency_class: Map.get(request, :idempotency_class, descriptor["idempotency_class"]),
        timeout_class: Map.get(request, :timeout_class, descriptor["timeout_class"]),
        mutating: mutating,
        input: Map.get(request, :input, %{}),
        approved_argument_digest: input_digest,
        lease_epoch: Map.fetch!(session_context, :lease_epoch),
        control_mode: normalize_string(Map.get(session_context, :control_mode, :autonomous)),
        health: normalize_string(Map.get(session_context, :health, :healthy))
      }

    action_hash = digest(action_core)
    approval_expires_at = approval_expires_at(request)
    required_scopes = Map.fetch!(descriptor, "required_scopes")

    with :ok <- ensure_tool_allowed_in_tier(descriptor, isolation_tier) do
      {capability_token, approved_argument_digest, token_claims} =
        maybe_issue_token(
          session_context,
          action_core,
          decision,
          approval_expires_at,
          required_scopes,
          request
        )

      {:ok,
       %{
         descriptor: descriptor,
         tool_schema_version: action_core.tool_schema_version,
         action_hash: action_hash,
         approved_argument_digest: approved_argument_digest,
         capability_token_ref: capability_token,
         capability_token_claims: token_claims,
         approval_required: decision == "require_approval",
         approval_expires_at: approval_expires_at,
         decision: decision,
         reason: reason_for(decision, dangerous_action_class, session_context),
         constraints: constraints_for(decision, session_context),
         risk_class: risk_class,
         dangerous_action_class: dangerous_action_class,
         mutating: mutating,
         worker_kind: action_core.worker_kind,
         isolation_tier: isolation_tier,
         worker_pool_id: action_core.worker_pool_id,
         dispatch_route_key: action_core.dispatch_route_key,
         idempotency_class: action_core.idempotency_class,
         timeout_class: action_core.timeout_class,
         required_scopes: required_scopes
       }}
    end
  rescue
    error in ArgumentError -> {:error, error.message}
  end

  @spec build_approval_request(map(), map(), map(), map()) :: map()
  def build_approval_request(session_context, action, decision, metadata \\ %{}) do
    approval_id =
      Map.get(
        metadata,
        :approval_id,
        "approval-" <> String.slice(Map.fetch!(decision, :action_hash), 0, 16)
      )

    %{
      approval_id: approval_id,
      tenant_id: Map.fetch!(session_context, :tenant_id),
      workspace_id: Map.fetch!(session_context, :workspace_id),
      session_id: Map.fetch!(session_context, :session_id),
      action_id: Map.fetch!(action, :action_id),
      action_hash: Map.fetch!(decision, :action_hash),
      status: "pending",
      risk_class: Map.fetch!(decision, :risk_class),
      dangerous_action_class: Map.fetch!(decision, :dangerous_action_class),
      expires_at: Map.fetch!(decision, :approval_expires_at),
      evidence_artifact_ids: Map.get(metadata, :evidence_artifact_ids, []),
      lease_epoch: Map.fetch!(session_context, :lease_epoch),
      requested_by: Map.get(metadata, :requested_by),
      tool_id: Map.fetch!(action, :tool_id),
      decided_by: nil
    }
  end

  @spec issue_capability_token(map(), map(), map()) :: %{token: String.t(), token_ref: String.t(), claims: map()}
  def issue_capability_token(session_context, action, opts \\ %{}) do
    expires_at = Map.get(opts, :expires_at, approval_expires_at(%{}))

    claims = %{
      tenant_id: Map.fetch!(session_context, :tenant_id),
      workspace_id: Map.fetch!(session_context, :workspace_id),
      session_id: Map.fetch!(session_context, :session_id),
      action_id: Map.fetch!(action, :action_id),
      tool_id: Map.fetch!(action, :tool_id),
      approved_argument_digest: Map.fetch!(action, :approved_argument_digest),
      dangerous_action_class: Map.fetch!(action, :dangerous_action_class),
      expires_at: expires_at,
      lease_epoch: Map.fetch!(session_context, :lease_epoch),
      side_effect_class: Map.get(opts, :side_effect_class, "browser_mutation"),
      scopes: Map.get(opts, :scopes, []),
      issued_to_worker_kind: Map.fetch!(action, :worker_kind)
    }

    CapabilityToken.mint(claims)
  end

  @spec approval_expires_at(map()) :: String.t()
  def approval_expires_at(request) when is_map(request) do
    Map.get_lazy(request, :approval_expires_at, fn ->
      DateTime.utc_now()
      |> DateTime.truncate(:second)
      |> DateTime.add(@approval_ttl_seconds, :second)
      |> DateTime.to_iso8601()
    end)
  end

  @spec digest(map()) :: String.t()
  def digest(value) when is_map(value) do
    value
    |> normalize()
    |> :erlang.term_to_binary()
    |> then(&:crypto.hash(:sha256, &1))
    |> Base.encode16(case: :lower)
  end

  defp maybe_issue_token(session_context, action_core, decision, approval_expires_at, required_scopes, request)
       when decision in ["allow", "allow_with_constraints", "require_approval", "deny"] do
    cond do
      decision == "allow_with_constraints" and action_core.mutating ->
        issue_token(session_context, action_core, approval_expires_at, required_scopes, request)

      true ->
        {nil, action_core.approved_argument_digest, nil}
    end
  end

  defp issue_token(session_context, action_core, approval_expires_at, required_scopes, request) do
    action = %{
      action_id: action_core.action_id,
      tool_id: action_core.tool_id,
      worker_kind: action_core.worker_kind,
      approved_argument_digest: action_core.approved_argument_digest,
      dangerous_action_class: action_core.dangerous_action_class
    }

    issued =
      issue_capability_token(
        session_context,
        action,
        %{
          expires_at: approval_expires_at,
          scopes: required_scopes,
          side_effect_class: Map.get(request, :side_effect_class, "browser_mutation")
        }
      )

    {issued.token, action_core.approved_argument_digest, issued.claims}
  end

  defp decide(session_context, mutating, dangerous_action_class) do
    health = normalize_string(Map.get(session_context, :health, :healthy))

    cond do
      health == "quarantined" ->
        "deny"

      true ->
        do_decide(session_context, mutating, dangerous_action_class)
    end
  end

  defp do_decide(_session_context, true, dangerous_action_class) do
    case DangerousActionCatalog.default_decision(dangerous_action_class) do
      "deny_without_explicit_policy" -> "deny"
      "require_approval" -> "require_approval"
      "allow_with_constraints" -> "allow_with_constraints"
      nil -> "require_approval"
      _other -> "require_approval"
    end
  end

  defp do_decide(session_context, false, nil) do
    if constrained_read_only?(session_context) do
      "allow_with_constraints"
    else
      "allow"
    end
  end

  defp do_decide(session_context, false, dangerous_action_class) when is_binary(dangerous_action_class) do
    decide(session_context, true, dangerous_action_class)
  end

  defp reason_for("allow", _dangerous_action_class, _session_context), do: "read_only_default"
  defp reason_for("deny", dangerous_action_class, %{health: :quarantined}), do: "session_quarantined:" <> to_string(dangerous_action_class || "all_actions")
  defp reason_for("deny", dangerous_action_class, _session_context), do: "denied_by_default:" <> to_string(dangerous_action_class || "unknown")
  defp reason_for("require_approval", dangerous_action_class, _session_context), do: "approval_required:" <> to_string(dangerous_action_class || "mutation")

  defp reason_for("allow_with_constraints", _dangerous_action_class, session_context) do
    health = normalize_string(Map.get(session_context, :health, :healthy))
    control_mode = normalize_string(Map.get(session_context, :control_mode, :autonomous))

    cond do
      health == "degraded" -> "degraded_mode_read_only"
      MapSet.member?(@constrained_control_modes, control_mode) -> "operator_supervised_read_only"
      true -> "explicit_constraints"
    end
  end

  defp constraints_for("allow_with_constraints", session_context) do
    health = normalize_string(Map.get(session_context, :health, :healthy))
    control_mode = normalize_string(Map.get(session_context, :control_mode, :autonomous))

    []
    |> maybe_append(health == "degraded", "manual_retry_only")
    |> maybe_append(MapSet.member?(@constrained_control_modes, control_mode), "operator_visible")
  end

  defp constraints_for("require_approval", _session_context), do: ["capability_token_required", "artifact_evidence_required"]
  defp constraints_for(_decision, _session_context), do: []

  defp constrained_read_only?(session_context) do
    normalize_string(Map.get(session_context, :health, :healthy)) == "degraded" or
      MapSet.member?(
        @constrained_control_modes,
        normalize_string(Map.get(session_context, :control_mode, :autonomous))
      )
  end

  defp dangerous_action_class(request, descriptor, true) do
    Map.get(request, :dangerous_action_class) ||
      Map.get(descriptor, "dangerous_action_class") ||
      "browser_write_medium"
  end

  defp dangerous_action_class(_request, descriptor, false), do: Map.get(descriptor, "dangerous_action_class")

  defp mutating?(request, descriptor) do
    Map.get(request, :mutating, false) or descriptor["risk_class"] in @effectful_risk_classes
  end

  defp derive_worker_kind(tool_id) do
    tool_id
    |> String.split(".", parts: 2)
    |> List.first()
  end

  defp ensure_tool_allowed_in_tier(descriptor, isolation_tier) do
    if isolation_tier in Map.get(descriptor, "allow_in_tiers", ["tier_a", "tier_b", "tier_c"]) do
      :ok
    else
      {:error, {:tool_not_allowed_in_tier, Map.fetch!(descriptor, "tool_id"), isolation_tier}}
    end
  end

  defp routing_metadata(session_context, worker_kind, isolation_tier) do
    route_key =
      case isolation_tier do
        "tier_b" -> "tenant-" <> route_segment(Map.fetch!(session_context, :tenant_id))
        "tier_c" -> "dedicated-" <> route_segment(Map.fetch!(session_context, :tenant_id))
        _ -> "shared"
      end

    %{
      isolation_tier: isolation_tier,
      dispatch_route_key: route_key,
      worker_pool_id: "#{worker_kind}:#{route_key}"
    }
  end

  defp route_segment(value) do
    value
    |> to_string()
    |> String.downcase()
    |> String.replace(~r/[^a-z0-9]+/, "-")
    |> String.trim("-")
    |> case do
      "" -> "default"
      segment -> segment
    end
  end

  defp normalize(value) when is_map(value) do
    value
    |> Enum.map(fn {key, item} -> {to_string(key), normalize(item)} end)
    |> Enum.sort_by(fn {key, _value} -> key end)
    |> Enum.into(%{})
  end

  defp normalize(value) when is_list(value), do: Enum.map(value, &normalize/1)
  defp normalize(value), do: value

  defp normalize_string(value) when is_atom(value), do: Atom.to_string(value)
  defp normalize_string(value) when is_binary(value), do: value

  defp maybe_append(list, true, value), do: list ++ [value]
  defp maybe_append(list, false, _value), do: list
end
