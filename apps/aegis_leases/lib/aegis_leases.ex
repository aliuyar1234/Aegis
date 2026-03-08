defmodule AegisLeases do
  @moduledoc """
  Boundary module for single-owner lease semantics, fencing, and adoption.

  The Phase 03 implementation lives under `Aegis.Leases`.
  """

  def claim(session_attrs), do: Aegis.Leases.claim(session_attrs)
  def claim(session_attrs, opts), do: Aegis.Leases.claim(session_attrs, opts)
  def current(session_id), do: Aegis.Leases.current(session_id)
  def authorize_command(session_id), do: Aegis.Leases.authorize_command(session_id)
  def authorize_command(session_id, opts), do: Aegis.Leases.authorize_command(session_id, opts)
  def adopt(session_id, attrs), do: Aegis.Leases.adopt(session_id, attrs)
  def adopt(session_id, attrs, opts), do: Aegis.Leases.adopt(session_id, attrs, opts)
  def mark_ambiguous(session_id, attrs), do: Aegis.Leases.mark_ambiguous(session_id, attrs)
end
