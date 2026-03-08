defmodule Aegis.Gateway.OperatorConsole do
  @moduledoc """
  Thin Phase 06 operator-console boundary over projection and observability read models.
  """

  alias Aegis.Obs.SystemHealth
  alias Aegis.Projection.{RunbookLinks, SessionDetail, SessionFleet, SessionReplay}
  alias Aegis.Runtime

  @spec session_fleet(map() | keyword()) :: %{
          sessions: [map()],
          system_health: map(),
          runbooks: [map()]
        }
  def session_fleet(filters \\ %{}) do
    all_sessions = SessionFleet.list()

    %{
      sessions: SessionFleet.list(filters),
      system_health: SystemHealth.overview(all_sessions),
      runbooks: RunbookLinks.for_surface("session-fleet")
    }
  end

  @spec session_view(String.t()) :: {:ok, map()} | {:error, term()}
  def session_view(session_id), do: SessionFleet.fetch(session_id)

  @spec session_detail(String.t()) :: {:ok, map()} | {:error, term()}
  def session_detail(session_id), do: SessionDetail.fetch(session_id)

  @spec session_replay(String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def session_replay(session_id, opts \\ []), do: SessionReplay.fetch(session_id, opts)

  @spec artifact_view(String.t(), String.t()) :: {:ok, map()} | {:error, term()}
  def artifact_view(session_id, artifact_id),
    do: SessionReplay.artifact_view(session_id, artifact_id)

  @spec operator_join(String.t(), String.t()) :: {:ok, map()} | {:error, term()}
  def operator_join(session_id, operator_id) do
    dispatch_operator(session_id, operator_id, {:operator_join, %{operator_id: operator_id}})
  end

  @spec add_operator_note(String.t(), String.t(), String.t(), String.t()) ::
          {:ok, map()} | {:error, term()}
  def add_operator_note(session_id, operator_id, note_ref, note_text) do
    dispatch_operator(
      session_id,
      operator_id,
      {:operator_add_note,
       %{
         operator_id: operator_id,
         note_ref: note_ref,
         note_text: note_text
       }}
    )
  end

  @spec pause_session(String.t(), String.t(), String.t()) :: {:ok, map()} | {:error, term()}
  def pause_session(session_id, operator_id, reason) do
    dispatch_operator(
      session_id,
      operator_id,
      {:operator_pause,
       %{
         operator_id: operator_id,
         reason: reason
       }}
    )
  end

  @spec abort_session(String.t(), String.t(), String.t()) :: {:ok, map()} | {:error, term()}
  def abort_session(session_id, operator_id, reason) do
    dispatch_operator(
      session_id,
      operator_id,
      {:operator_abort,
       %{
         operator_id: operator_id,
         reason: reason
       }}
    )
  end

  @spec take_control(String.t(), String.t(), String.t()) :: {:ok, map()} | {:error, term()}
  def take_control(session_id, operator_id, reason) do
    dispatch_operator(
      session_id,
      operator_id,
      {:operator_take_control,
       %{
         operator_id: operator_id,
         reason: reason
      }}
    )
  end

  @spec grant_approval(String.t(), String.t(), String.t(), String.t()) ::
          {:ok, map()} | {:error, term()}
  def grant_approval(session_id, operator_id, approval_id, action_hash) do
    dispatch_operator(
      session_id,
      operator_id,
      {:grant_approval,
       %{
         approval_id: approval_id,
         action_hash: action_hash,
         operator_id: operator_id,
         decided_by: operator_id
       }}
    )
  end

  @spec deny_approval(String.t(), String.t(), String.t(), String.t(), String.t()) ::
          {:ok, map()} | {:error, term()}
  def deny_approval(session_id, operator_id, approval_id, action_hash, reason) do
    dispatch_operator(
      session_id,
      operator_id,
      {:deny_approval,
       %{
         approval_id: approval_id,
         action_hash: action_hash,
         operator_id: operator_id,
         decided_by: operator_id,
         reason: reason
       }}
    )
  end

  @spec return_control(String.t(), String.t(), String.t(), atom()) ::
          {:ok, map()} | {:error, term()}
  def return_control(session_id, operator_id, return_context, control_mode \\ :autonomous) do
    dispatch_operator(
      session_id,
      operator_id,
      {:operator_return_control,
       %{
         operator_id: operator_id,
         return_context: return_context,
         control_mode: control_mode
       }}
    )
  end

  @spec system_health_overview() :: map()
  def system_health_overview do
    SessionFleet.list()
    |> SystemHealth.overview()
    |> Map.put(:runbooks, RunbookLinks.for_surface("session-fleet"))
  end

  defp dispatch_operator(session_id, operator_id, command) do
    with {:ok, lease} <- Runtime.lease(session_id) do
      Runtime.dispatch(
        session_id,
        command,
        owner_node: lease.owner_node,
        lease_epoch: lease.lease_epoch,
        actor_kind: "operator",
        actor_id: operator_id
      )
    end
  end
end
