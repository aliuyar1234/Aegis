defmodule Aegis.Policy.Authorizer do
  @moduledoc """
  Phase 09 RBAC/ABAC authorization boundary for operator and API control surfaces.
  """

  alias Aegis.Policy.{AbacAttributes, RbacRoles}

  @privileged_roles MapSet.new(["platform_admin"])
  @interactive_roles MapSet.new(["platform_admin", "operator"])
  @production_envs MapSet.new(["prod", "production"])
  @resource_attributes ~w(tenant_id workspace_id environment dangerous_action_class reveal_redacted)a

  @spec authorize_surface(map(), String.t(), map()) :: {:ok, map()} | {:error, term()}
  def authorize_surface(auth_context, surface, resource \\ %{})
      when is_binary(surface) and is_map(resource) do
    auth = normalize_auth_context(auth_context)
    resource = normalize_resource(resource)

    with {:ok, role} <- RbacRoles.fetch(auth.role),
         :ok <- ensure_known_attributes(auth, resource),
         :ok <- ensure_surface_allowed(auth, role, surface),
         :ok <- ensure_scope_allowed(auth, role, resource),
         :ok <- ensure_environment_allowed(auth, role, surface),
         :ok <- ensure_redaction_allowed(auth, role, resource) do
      {:ok,
       %{
         role: Map.fetch!(role, "id"),
         surface: surface,
         tenant_id: Map.get(resource, :tenant_id, Map.get(auth, :tenant_id)),
         workspace_id: Map.get(resource, :workspace_id, Map.get(auth, :workspace_id)),
         allowed_workspaces: Map.get(auth, :allowed_workspaces, []),
         can_reveal_redacted: can_reveal_redacted?(auth, role)
       }}
    end
  end

  @spec scope_filters(map(), String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def scope_filters(auth_context, surface, filters \\ %{}) do
    filters = filters |> Map.new() |> normalize_resource()

    with {:ok, _decision} <- authorize_surface(auth_context, surface, filters) do
      auth = normalize_auth_context(auth_context)

      {:ok,
       filters
       |> maybe_put(:tenant_id, scoped_tenant_id(auth))
       |> maybe_put(:workspace_id, scoped_workspace_id(auth))}
    end
  end

  @spec authorize_operator_action(map(), String.t(), map()) :: {:ok, map()} | {:error, term()}
  def authorize_operator_action(auth_context, action, resource)
      when is_binary(action) and is_map(resource) do
    with {:ok, decision} <- authorize_surface(auth_context, "session-detail", resource),
         :ok <- ensure_interactive_role(decision.role, action) do
      {:ok, decision}
    end
  end

  @spec authorize_approval_action(map(), String.t(), map()) :: {:ok, map()} | {:error, term()}
  def authorize_approval_action(auth_context, action, approval)
      when is_binary(action) and is_map(approval) do
    with {:ok, decision} <- authorize_surface(auth_context, "approvals-queue", approval),
         :ok <- ensure_approver_for_class(decision.role, approval, action) do
      {:ok, decision}
    end
  end

  @spec filter_allowed_workspaces([map()], map()) :: [map()]
  def filter_allowed_workspaces(resources, auth_context) when is_list(resources) do
    auth = normalize_auth_context(auth_context)
    allowed_workspaces = Map.get(auth, :allowed_workspaces, [])

    if privileged?(Map.get(auth, :role)) or allowed_workspaces == [] do
      resources
    else
      Enum.filter(resources, &Map.get(&1, :workspace_id) in allowed_workspaces)
    end
  end

  @spec redact_controls(map(), map()) :: map()
  def redact_controls(controls, auth_context) when is_map(controls) do
    auth = normalize_auth_context(auth_context)

    Map.merge(controls, %{
      join: interactive?(auth.role) and Map.get(controls, :join, false),
      add_note: interactive?(auth.role) and Map.get(controls, :add_note, false),
      pause: interactive?(auth.role) and Map.get(controls, :pause, false),
      abort: interactive?(auth.role) and Map.get(controls, :abort, false),
      take_control: interactive?(auth.role) and Map.get(controls, :take_control, false),
      return_control: interactive?(auth.role) and Map.get(controls, :return_control, false)
    })
  end

  @spec allow_approval_controls?(map(), [map()]) :: boolean()
  def allow_approval_controls?(auth_context, approvals) when is_list(approvals) do
    approvals != [] and Enum.all?(approvals, &approval_class_allowed?(normalize_auth_context(auth_context).role, &1))
  end

  defp ensure_known_attributes(auth, resource) do
    known = MapSet.new(AbacAttributes.ids())

    auth_attributes =
      [:tenant_id, :workspace_id, :environment]
      |> Enum.filter(&Map.get(auth, &1))
      |> Enum.map(&Atom.to_string/1)
      |> MapSet.new()

    resource_attributes =
      @resource_attributes
      |> Enum.filter(&Map.get(resource, &1))
      |> Enum.map(&Atom.to_string/1)
      |> MapSet.new()

    unknown = MapSet.union(auth_attributes, resource_attributes) |> MapSet.difference(known)

    if MapSet.size(unknown) == 0 do
      :ok
    else
      {:error, {:unknown_abac_attributes, unknown |> MapSet.to_list() |> Enum.sort()}}
    end
  end

  defp ensure_surface_allowed(auth, role, surface) do
    allowed = Map.get(role, "allowed_surfaces", [])

    cond do
      privileged?(auth.role) ->
        :ok

      surface in allowed ->
        :ok

      surface == "session-detail" and "dev-session-detail" in allowed and non_production?(auth) ->
        :ok

      true ->
        {:error, {:forbidden, :surface_not_allowed}}
    end
  end

  defp ensure_scope_allowed(auth, role, resource) do
    if privileged?(Map.fetch!(role, "id")) do
      :ok
    else
      cond do
        is_nil(Map.get(auth, :tenant_id)) ->
          {:error, {:forbidden, :missing_tenant_scope}}

        present?(Map.get(resource, :tenant_id)) and Map.get(resource, :tenant_id) != Map.get(auth, :tenant_id) ->
          {:error, {:forbidden, :tenant_scope_mismatch}}

        workspace_scope_mismatch?(auth, Map.get(resource, :workspace_id)) ->
          {:error, {:forbidden, :workspace_scope_mismatch}}

        true ->
          :ok
      end
    end
  end

  defp ensure_environment_allowed(auth, role, surface) do
    cond do
      privileged?(Map.fetch!(role, "id")) ->
        :ok

      Map.fetch!(role, "id") == "developer" and surface == "session-detail" and non_production?(auth) ->
        :ok

      Map.fetch!(role, "id") == "developer" ->
        {:error, {:forbidden, :production_session_access_denied}}

      true ->
        :ok
    end
  end

  defp ensure_redaction_allowed(auth, role, resource) do
    if Map.get(resource, :reveal_redacted, false) and not can_reveal_redacted?(auth, role) do
      {:error, {:forbidden, :redacted_reveal_not_allowed}}
    else
      :ok
    end
  end

  defp ensure_interactive_role(role_id, _action) do
    if interactive?(role_id) do
      :ok
    else
      {:error, {:forbidden, :operator_action_not_allowed}}
    end
  end

  defp ensure_approver_for_class(role_id, approval, _action) do
    if approval_class_allowed?(role_id, approval) do
      :ok
    else
      {:error, {:forbidden, :approval_class_not_allowed}}
    end
  end

  defp approval_class_allowed?(role_id, approval) do
    role = RbacRoles.fetch!(role_id)
    approvals = Map.get(role, "can_approve", [])
    class = Map.get(approval, :dangerous_action_class)

    "all" in approvals or class in approvals
  end

  defp normalize_auth_context(auth_context) do
    normalized =
      auth_context
      |> Map.new()
      |> normalize_resource()

    normalized
    |> Map.put(:role, Map.get(normalized, :role))
    |> Map.put(:actor_id, Map.get(normalized, :actor_id))
    |> Map.put(:allowed_workspaces, normalize_allowed_workspaces(Map.get(normalized, :allowed_workspaces)))
    |> Map.put_new(:environment, Map.get(normalized, :environment) || "production")
  end

  defp normalize_resource(resource) do
    resource
    |> Enum.map(fn {key, value} -> {normalize_key(key), value} end)
    |> Enum.into(%{})
  end

  defp normalize_allowed_workspaces(nil), do: []
  defp normalize_allowed_workspaces(workspaces) when is_list(workspaces), do: workspaces
  defp normalize_allowed_workspaces(workspace) when is_binary(workspace), do: [workspace]

  defp scoped_tenant_id(auth) do
    if privileged?(Map.get(auth, :role)), do: nil, else: Map.get(auth, :tenant_id)
  end

  defp scoped_workspace_id(auth) do
    cond do
      privileged?(Map.get(auth, :role)) -> nil
      Map.get(auth, :allowed_workspaces, []) != [] -> nil
      true -> Map.get(auth, :workspace_id)
    end
  end

  defp can_reveal_redacted?(auth, role) do
    Map.get(role, "can_reveal_redacted", false) and Map.get(auth, :reveal_redacted, false)
  end

  defp workspace_scope_mismatch?(_auth, nil), do: false

  defp workspace_scope_mismatch?(auth, workspace_id) do
    allowed_workspaces = Map.get(auth, :allowed_workspaces, [])

    cond do
      allowed_workspaces != [] -> workspace_id not in allowed_workspaces
      present?(Map.get(auth, :workspace_id)) -> workspace_id != Map.get(auth, :workspace_id)
      true -> false
    end
  end

  defp privileged?(role_id), do: MapSet.member?(@privileged_roles, role_id)
  defp interactive?(role_id), do: MapSet.member?(@interactive_roles, role_id)
  defp non_production?(auth), do: not MapSet.member?(@production_envs, to_string(Map.get(auth, :environment)))

  defp maybe_put(map, _key, nil), do: map
  defp maybe_put(map, key, value), do: Map.put(map, key, value)

  defp normalize_key(key) when is_atom(key), do: key

  defp normalize_key(key) when is_binary(key) do
    try do
      String.to_existing_atom(key)
    rescue
      ArgumentError -> key
    end
  end

  defp present?(value) when value in [nil, ""], do: false
  defp present?(_value), do: true
end
