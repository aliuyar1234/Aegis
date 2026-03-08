defmodule AegisRuntime do
  @moduledoc """
  Compatibility wrapper for the `aegis_runtime` umbrella application.

  The Phase 01 runtime implementation lives under `Aegis.Runtime`.
  """

  def start_session(attrs), do: Aegis.Runtime.start_session(attrs)
  def dispatch(session_id, command), do: Aegis.Runtime.dispatch(session_id, command)
  def dispatch(session_id, command, opts), do: Aegis.Runtime.dispatch(session_id, command, opts)
  def adopt(session_id, attrs), do: Aegis.Runtime.adopt(session_id, attrs)
  def report_lease_ambiguity(session_id, attrs), do: Aegis.Runtime.report_lease_ambiguity(session_id, attrs)
  def snapshot(session_id), do: Aegis.Runtime.snapshot(session_id)
  def projection(session_id), do: Aegis.Runtime.projection(session_id)
  def events(session_id), do: Aegis.Runtime.events(session_id)
  def lease(session_id), do: Aegis.Runtime.lease(session_id)
end
