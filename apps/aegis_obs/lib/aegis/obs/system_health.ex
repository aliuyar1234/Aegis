defmodule Aegis.Obs.SystemHealth do
  @moduledoc """
  Phase 06 system-health rollup for operator fleet surfaces.

  This summary is derived from stable session views plus worker-registry state.
  It is an operator aid, not authoritative session truth.
  """

  alias Aegis.ExecutionBridge

  @spec overview([map()], [map()]) :: map()
  def overview(session_views, worker_registrations \\ ExecutionBridge.worker_registrations()) do
    %{
      status: overall_status(session_views, worker_registrations),
      sessions: %{
        total: length(session_views),
        waiting: Enum.count(session_views, &(&1.wait_reason != "none")),
        approval_waits: Enum.count(session_views, &approval_wait?/1),
        fenced: Enum.count(session_views, & &1.fenced),
        by_health: count_by(session_views, & &1.health),
        by_phase: count_by(session_views, & &1.phase)
      },
      workers: %{
        total: length(worker_registrations),
        available_capacity: Enum.sum(Enum.map(worker_registrations, &Map.get(&1, :available_capacity, 0))),
        advertised_capacity: Enum.sum(Enum.map(worker_registrations, &Map.get(&1, :advertised_capacity, 0))),
        by_kind: count_by(worker_registrations, &Map.get(&1, :worker_kind, "unknown")),
        by_status: count_by(worker_registrations, &Map.get(&1, :status, "unknown"))
      }
    }
  end

  defp approval_wait?(session) do
    session.wait_reason == "approval" or session.pending_approvals != []
  end

  defp overall_status(session_views, worker_registrations) do
    cond do
      Enum.any?(session_views, &(&1.health == "quarantined")) ->
        "quarantined"

      Enum.any?(worker_registrations, &(Map.get(&1, :status) == "quarantined")) ->
        "quarantined"

      Enum.any?(session_views, &(&1.health == "degraded" or &1.fenced)) ->
        "degraded"

      Enum.any?(worker_registrations, &(Map.get(&1, :status, "active") != "active")) ->
        "degraded"

      true ->
        "healthy"
    end
  end

  defp count_by(entries, key_fun) do
    Enum.reduce(entries, %{}, fn entry, acc ->
      key = key_fun.(entry)
      Map.update(acc, key, 1, &(&1 + 1))
    end)
  end
end
