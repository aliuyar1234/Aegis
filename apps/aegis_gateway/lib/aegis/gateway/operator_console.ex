defmodule Aegis.Gateway.OperatorConsole do
  @moduledoc """
  Phase 09 operator/API boundary over projection, observability, and policy authz.
  """

  alias Aegis.Obs.SystemHealth
  alias Aegis.Projection.{RunbookLinks, SessionDetail, SessionFleet, SessionReplay}
  alias Aegis.Runtime

  @spec session_fleet(map() | keyword(), map() | keyword()) ::
          {:ok, %{sessions: [map()], system_health: map(), runbooks: [map()]}} | {:error, term()}
  def session_fleet(auth_context, filters \\ %{}) do
    with {:ok, scoped_filters} <- AegisPolicy.scope_filters(auth_context, "session-fleet", filters) do
      scope = projection_scope(scoped_filters)

      all_sessions =
        SessionFleet.list(%{}, scope)
        |> AegisPolicy.filter_allowed_workspaces(auth_context)

      sessions =
        scoped_filters
        |> SessionFleet.list(scope)
        |> AegisPolicy.filter_allowed_workspaces(auth_context)

      {:ok,
       %{
         sessions: sessions,
         system_health: SystemHealth.overview(all_sessions),
         runbooks: RunbookLinks.for_surface("session-fleet")
       }}
    end
  end

  @spec session_view(map() | keyword(), String.t()) :: {:ok, map()} | {:error, term()}
  def session_view(auth_context, session_id) do
    with {:ok, view} <- load_session_view(auth_context, "session-detail", session_id) do
      {:ok, view}
    end
  end

  @spec session_detail(map() | keyword(), String.t()) :: {:ok, map()} | {:error, term()}
  def session_detail(auth_context, session_id) do
    with {:ok, detail} <- load_session_detail(auth_context, "session-detail", session_id) do
      controls =
        detail.controls
        |> AegisPolicy.redact_controls(auth_context)
        |> Map.put(
          :grant_approval,
          Map.get(detail.controls, :grant_approval, false) and
            AegisPolicy.allow_approval_controls?(auth_context, detail.approvals)
        )
        |> Map.put(
          :deny_approval,
          Map.get(detail.controls, :deny_approval, false) and
            AegisPolicy.allow_approval_controls?(auth_context, detail.approvals)
        )

      {:ok, Map.put(detail, :controls, controls)}
    end
  end

  @spec session_replay(map() | keyword(), String.t(), map() | keyword()) ::
          {:ok, map()} | {:error, term()}
  def session_replay(auth_context, session_id, opts \\ []) do
    with {:ok, scope} <- AegisPolicy.scope_filters(auth_context, "replay", %{}),
         {:ok, replay} <- SessionReplay.fetch(session_id, opts, projection_scope(scope)),
         :ok <-
           authorize_loaded_resource(
             auth_context,
             "replay",
             replay.session
           ) do
      {:ok, replay}
    else
      {:error, {:forbidden, :tenant_scope_mismatch}} -> {:error, :unknown_session}
      {:error, {:forbidden, :workspace_scope_mismatch}} -> {:error, :unknown_session}
      other -> other
    end
  end

  @spec artifact_view(map() | keyword(), String.t(), String.t()) :: {:ok, map()} | {:error, term()}
  def artifact_view(auth_context, session_id, artifact_id) do
    with {:ok, scope} <- AegisPolicy.scope_filters(auth_context, "replay", %{}),
         {:ok, replay} <- SessionReplay.fetch(session_id, [], projection_scope(scope)),
         {:ok, artifact} <- SessionReplay.artifact_view(session_id, artifact_id, projection_scope(scope)),
         :ok <- authorize_loaded_resource(auth_context, "replay", replay.session) do
      {:ok, artifact}
    else
      {:error, {:forbidden, :tenant_scope_mismatch}} -> {:error, :unknown_session}
      {:error, {:forbidden, :workspace_scope_mismatch}} -> {:error, :unknown_session}
      other -> other
    end
  end

  @spec operator_join(map() | keyword(), String.t()) :: {:ok, map()} | {:error, term()}
  def operator_join(auth_context, session_id) do
    dispatch_operator(auth_context, session_id, "operator_join", fn actor_id ->
      {:operator_join, %{operator_id: actor_id}}
    end)
  end

  @spec add_operator_note(map() | keyword(), String.t(), String.t(), String.t()) ::
          {:ok, map()} | {:error, term()}
  def add_operator_note(auth_context, session_id, note_ref, note_text) do
    dispatch_operator(auth_context, session_id, "operator_add_note", fn actor_id ->
      {:operator_add_note,
       %{
         operator_id: actor_id,
         note_ref: note_ref,
         note_text: note_text
       }}
    end)
  end

  @spec pause_session(map() | keyword(), String.t(), String.t()) :: {:ok, map()} | {:error, term()}
  def pause_session(auth_context, session_id, reason) do
    dispatch_operator(auth_context, session_id, "operator_pause", fn actor_id ->
      {:operator_pause,
       %{
         operator_id: actor_id,
         reason: reason
       }}
    end)
  end

  @spec abort_session(map() | keyword(), String.t(), String.t()) :: {:ok, map()} | {:error, term()}
  def abort_session(auth_context, session_id, reason) do
    dispatch_operator(auth_context, session_id, "operator_abort", fn actor_id ->
      {:operator_abort,
       %{
         operator_id: actor_id,
         reason: reason
       }}
    end)
  end

  @spec take_control(map() | keyword(), String.t(), String.t()) :: {:ok, map()} | {:error, term()}
  def take_control(auth_context, session_id, reason) do
    dispatch_operator(auth_context, session_id, "operator_take_control", fn actor_id ->
      {:operator_take_control,
       %{
         operator_id: actor_id,
         reason: reason
       }}
    end)
  end

  @spec grant_approval(map() | keyword(), String.t(), String.t(), String.t()) ::
          {:ok, map()} | {:error, term()}
  def grant_approval(auth_context, session_id, approval_id, action_hash) do
    with {:ok, detail} <- load_session_detail(auth_context, "approvals-queue", session_id),
         {:ok, approval} <- fetch_approval(detail.approvals, approval_id),
         {:ok, _decision} <- AegisPolicy.authorize_approval_action(auth_context, "grant_approval", approval) do
      dispatch_approval(auth_context, session_id, {:grant_approval, approval_id, action_hash})
    end
  end

  @spec deny_approval(map() | keyword(), String.t(), String.t(), String.t(), String.t()) ::
          {:ok, map()} | {:error, term()}
  def deny_approval(auth_context, session_id, approval_id, action_hash, reason) do
    with {:ok, detail} <- load_session_detail(auth_context, "approvals-queue", session_id),
         {:ok, approval} <- fetch_approval(detail.approvals, approval_id),
         {:ok, _decision} <- AegisPolicy.authorize_approval_action(auth_context, "deny_approval", approval) do
      dispatch_approval(auth_context, session_id, {:deny_approval, approval_id, action_hash, reason})
    end
  end

  @spec return_control(map() | keyword(), String.t(), String.t(), atom()) ::
          {:ok, map()} | {:error, term()}
  def return_control(auth_context, session_id, return_context, control_mode \\ :autonomous) do
    dispatch_operator(auth_context, session_id, "operator_return_control", fn actor_id ->
      {:operator_return_control,
       %{
         operator_id: actor_id,
         return_context: return_context,
         control_mode: control_mode
       }}
    end)
  end

  @spec system_health_overview(map() | keyword()) :: {:ok, map()} | {:error, term()}
  def system_health_overview(auth_context) do
    with {:ok, fleet} <- session_fleet(auth_context) do
      {:ok,
       fleet.system_health
       |> Map.put(:runbooks, RunbookLinks.for_surface("session-fleet"))}
    end
  end

  defp dispatch_operator(auth_context, session_id, action, command_builder) do
    with {:ok, detail} <- load_session_detail(auth_context, "session-detail", session_id),
         {:ok, _decision} <-
           AegisPolicy.authorize_operator_action(auth_context, action, session_scope_from_projection(detail.session)),
         {:ok, lease} <- Runtime.lease(session_id) do
      Runtime.dispatch(
        session_id,
        command_builder.(actor_id!(auth_context)),
        owner_node: lease.owner_node,
        lease_epoch: lease.lease_epoch,
        actor_kind: "operator",
        actor_id: actor_id!(auth_context)
      )
    end
  end

  defp dispatch_approval(auth_context, session_id, {:grant_approval, approval_id, action_hash}) do
    with {:ok, lease} <- Runtime.lease(session_id) do
      Runtime.dispatch(
        session_id,
        {:grant_approval,
         %{
           approval_id: approval_id,
           action_hash: action_hash,
           operator_id: actor_id!(auth_context),
           decided_by: actor_id!(auth_context)
         }},
        owner_node: lease.owner_node,
        lease_epoch: lease.lease_epoch,
        actor_kind: "operator",
        actor_id: actor_id!(auth_context)
      )
    end
  end

  defp dispatch_approval(auth_context, session_id, {:deny_approval, approval_id, action_hash, reason}) do
    with {:ok, lease} <- Runtime.lease(session_id) do
      Runtime.dispatch(
        session_id,
        {:deny_approval,
         %{
           approval_id: approval_id,
           action_hash: action_hash,
           operator_id: actor_id!(auth_context),
           decided_by: actor_id!(auth_context),
           reason: reason
         }},
        owner_node: lease.owner_node,
        lease_epoch: lease.lease_epoch,
        actor_kind: "operator",
        actor_id: actor_id!(auth_context)
      )
    end
  end

  defp load_session_view(auth_context, surface, session_id) do
    with {:ok, scope} <- AegisPolicy.scope_filters(auth_context, surface, %{}),
         {:ok, view} <- SessionFleet.fetch(session_id, projection_scope(scope)),
         :ok <- authorize_loaded_resource(auth_context, surface, view) do
      {:ok, view}
    else
      {:error, {:forbidden, :tenant_scope_mismatch}} -> {:error, :unknown_session}
      {:error, {:forbidden, :workspace_scope_mismatch}} -> {:error, :unknown_session}
      other -> other
    end
  end

  defp load_session_detail(auth_context, surface, session_id) do
    with {:ok, scope} <- AegisPolicy.scope_filters(auth_context, surface, %{}),
         {:ok, detail} <- SessionDetail.fetch(session_id, projection_scope(scope)),
         :ok <- authorize_loaded_resource(auth_context, surface, detail.session) do
      {:ok, detail}
    else
      {:error, {:forbidden, :tenant_scope_mismatch}} -> {:error, :unknown_session}
      {:error, {:forbidden, :workspace_scope_mismatch}} -> {:error, :unknown_session}
      other -> other
    end
  end

  defp authorize_loaded_resource(auth_context, surface, session_projection) do
    AegisPolicy.authorize_surface(
      auth_context,
      surface,
      session_scope_from_projection(session_projection)
    )
    |> decision_to_ok(:unknown_session)
  end

  defp fetch_approval(approvals, approval_id) do
    case Enum.find(approvals, &(&1.approval_id == approval_id)) do
      nil -> {:error, :unknown_approval}
      approval -> {:ok, approval}
    end
  end

  defp decision_to_ok({:ok, _decision}, _fallback), do: :ok

  defp decision_to_ok({:error, {:forbidden, :tenant_scope_mismatch}}, fallback),
    do: {:error, fallback}

  defp decision_to_ok({:error, {:forbidden, :workspace_scope_mismatch}}, fallback),
    do: {:error, fallback}

  defp decision_to_ok({:error, reason}, _fallback), do: {:error, reason}

  defp session_scope_from_projection(session_projection) do
    %{
      tenant_id: Map.fetch!(session_projection, :tenant_id),
      workspace_id: Map.fetch!(session_projection, :workspace_id)
    }
  end

  defp projection_scope(scope) do
    %{
      tenant_id: Map.get(scope, :tenant_id),
      workspace_id: Map.get(scope, :workspace_id)
    }
  end

  defp actor_id!(auth_context) do
    auth = Map.new(auth_context)

    Map.get(auth, :actor_id) || Map.get(auth, "actor_id") ||
      raise ArgumentError, "missing actor_id in auth context"
  end
end
