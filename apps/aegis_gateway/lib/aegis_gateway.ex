defmodule AegisGateway do
  @moduledoc """
  Boundary module for API and operator entry surfaces.

  Gateway code must consume runtime APIs and projections without bypassing the
  `SessionKernel`.
  """

  def session_fleet(auth_context, filters \\ %{}),
    do: Aegis.Gateway.OperatorConsole.session_fleet(auth_context, filters)

  def session_view(auth_context, session_id),
    do: Aegis.Gateway.OperatorConsole.session_view(auth_context, session_id)

  def session_detail(auth_context, session_id),
    do: Aegis.Gateway.OperatorConsole.session_detail(auth_context, session_id)

  def session_replay(auth_context, session_id, opts \\ []),
    do: Aegis.Gateway.OperatorConsole.session_replay(auth_context, session_id, opts)

  def artifact_view(auth_context, session_id, artifact_id),
    do: Aegis.Gateway.OperatorConsole.artifact_view(auth_context, session_id, artifact_id)

  def operator_join(auth_context, session_id),
    do: Aegis.Gateway.OperatorConsole.operator_join(auth_context, session_id)

  def add_operator_note(auth_context, session_id, note_ref, note_text),
    do: Aegis.Gateway.OperatorConsole.add_operator_note(auth_context, session_id, note_ref, note_text)

  def pause_session(auth_context, session_id, reason),
    do: Aegis.Gateway.OperatorConsole.pause_session(auth_context, session_id, reason)

  def abort_session(auth_context, session_id, reason),
    do: Aegis.Gateway.OperatorConsole.abort_session(auth_context, session_id, reason)

  def take_control(auth_context, session_id, reason),
    do: Aegis.Gateway.OperatorConsole.take_control(auth_context, session_id, reason)

  def return_control(auth_context, session_id, return_context, control_mode \\ :autonomous),
    do: Aegis.Gateway.OperatorConsole.return_control(auth_context, session_id, return_context, control_mode)

  def grant_approval(auth_context, session_id, approval_id, action_hash),
    do: Aegis.Gateway.OperatorConsole.grant_approval(auth_context, session_id, approval_id, action_hash)

  def deny_approval(auth_context, session_id, approval_id, action_hash, reason),
    do: Aegis.Gateway.OperatorConsole.deny_approval(auth_context, session_id, approval_id, action_hash, reason)

  def system_health_overview(auth_context),
    do: Aegis.Gateway.OperatorConsole.system_health_overview(auth_context)
end
