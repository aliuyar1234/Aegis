defmodule AegisProjection do
  @moduledoc """
  Boundary module for stable query/read models used by operator surfaces.

  Phase 01 defines projection fields inside `aegis_runtime`, but read-optimized,
  independently materialized projections remain the responsibility of this app.
  """

  def session_fleet(filters \\ %{}), do: Aegis.Projection.SessionFleet.list(filters)
  def session_view(session_id), do: Aegis.Projection.SessionFleet.fetch(session_id)
  def session_detail(session_id), do: Aegis.Projection.SessionDetail.fetch(session_id)
  def session_replay(session_id, opts \\ []), do: Aegis.Projection.SessionReplay.fetch(session_id, opts)
  def artifact_view(session_id, artifact_id), do: Aegis.Projection.SessionReplay.artifact_view(session_id, artifact_id)
end
