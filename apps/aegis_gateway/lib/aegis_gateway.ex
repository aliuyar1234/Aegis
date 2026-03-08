defmodule AegisGateway do
  @moduledoc """
  Boundary module for API and operator entry surfaces.

  Gateway code must consume runtime APIs and projections without bypassing the
  `SessionKernel`.
  """

  def session_fleet(filters \\ %{}), do: Aegis.Gateway.OperatorConsole.session_fleet(filters)
  def session_view(session_id), do: Aegis.Gateway.OperatorConsole.session_view(session_id)
  def session_detail(session_id), do: Aegis.Gateway.OperatorConsole.session_detail(session_id)
  def session_replay(session_id, opts \\ []), do: Aegis.Gateway.OperatorConsole.session_replay(session_id, opts)
  def artifact_view(session_id, artifact_id), do: Aegis.Gateway.OperatorConsole.artifact_view(session_id, artifact_id)
  def operator_join(session_id, operator_id), do: Aegis.Gateway.OperatorConsole.operator_join(session_id, operator_id)
  def add_operator_note(session_id, operator_id, note_ref, note_text), do: Aegis.Gateway.OperatorConsole.add_operator_note(session_id, operator_id, note_ref, note_text)
  def pause_session(session_id, operator_id, reason), do: Aegis.Gateway.OperatorConsole.pause_session(session_id, operator_id, reason)
  def abort_session(session_id, operator_id, reason), do: Aegis.Gateway.OperatorConsole.abort_session(session_id, operator_id, reason)
  def take_control(session_id, operator_id, reason), do: Aegis.Gateway.OperatorConsole.take_control(session_id, operator_id, reason)
  def return_control(session_id, operator_id, return_context, control_mode \\ :autonomous), do: Aegis.Gateway.OperatorConsole.return_control(session_id, operator_id, return_context, control_mode)
  def system_health_overview, do: Aegis.Gateway.OperatorConsole.system_health_overview()
end
