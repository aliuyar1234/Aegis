defmodule Aegis.Projection.SessionFleet do
  @moduledoc """
  Stable fleet-query surface for Phase 06 operator session inspection.

  Source of truth:
  - phase doc: `docs/exec-plans/active/PHASE-06-operator-console.md`
  - product spec: `docs/product-specs/operator-console.md`
  - acceptance: `AC-024`, `AC-025`
  - tests: `TS-008` (`python3 scripts/run_elixir_suite.py TS-008`)

  This module builds operator session rows from authoritative replay state and
  must not introduce hidden UI-only state.
  """

  alias Aegis.Events
  alias Aegis.Runtime
  alias Aegis.Runtime.Projection

  @exact_match_filters ~w(tenant_id workspace_id session_id phase control_mode health wait_reason owner_node)a
  @boolean_filters ~w(fenced has_pending_approval has_in_flight_action)a

  @spec list(map() | keyword(), map() | keyword()) :: [map()]
  def list(filters \\ %{}, scope \\ %{}) do
    filters = normalize_filters(filters)
    scope = normalize_filters(scope)

    Events.sessions(scope)
    |> Enum.map(&build_view(&1, scope))
    |> Enum.reject(&is_nil/1)
    |> Enum.filter(&matches_filters?(&1, filters))
    |> Enum.sort_by(&sort_key/1)
  end

  @spec fetch(String.t(), map() | keyword()) :: {:ok, map()} | {:error, term()}
  def fetch(session_id, scope \\ %{}) when is_binary(session_id) do
    with {:ok, replay} <- Runtime.historical_replay(session_id, scope) do
      {:ok, Projection.from_snapshot(replay.replay_state)}
    end
  end

  defp build_view(session_row, scope) do
    case Runtime.historical_replay(session_row.session_id, scope) do
      {:ok, replay} -> Projection.from_snapshot(replay.replay_state)
      {:error, _reason} -> nil
    end
  end

  defp matches_filters?(session, filters) do
    Enum.all?(@exact_match_filters, fn key ->
      expected = Map.get(filters, key)
      is_nil(expected) or Map.get(session, key) == expected
    end) and
      Enum.all?(@boolean_filters, fn key ->
        expected = Map.get(filters, key)
        is_nil(expected) or boolean_filter_match?(session, key, expected)
      end) and
      session_id_match?(session, Map.get(filters, :session_ids)) and
      query_match?(session, Map.get(filters, :query))
  end

  defp boolean_filter_match?(session, :fenced, expected), do: session.fenced == expected

  defp boolean_filter_match?(session, :has_pending_approval, expected) do
    (session.pending_approvals != []) == expected
  end

  defp boolean_filter_match?(session, :has_in_flight_action, expected) do
    (session.in_flight_actions != []) == expected
  end

  defp session_id_match?(_session, nil), do: true

  defp session_id_match?(session, session_ids) when is_list(session_ids) do
    session.session_id in session_ids
  end

  defp query_match?(_session, nil), do: true
  defp query_match?(_session, ""), do: true

  defp query_match?(session, query) do
    normalized_query = String.downcase(query)

    [session.session_id, session.tenant_id, session.workspace_id, session.owner_node]
    |> Enum.any?(fn value -> String.contains?(String.downcase(value), normalized_query) end)
  end

  defp normalize_filters(filters) do
    filters
    |> Map.new()
    |> Enum.into(%{}, fn
      {:session_ids, value} when is_binary(value) -> {:session_ids, [value]}
      pair -> pair
    end)
  end

  defp sort_key(session) do
    {
      health_rank(session.health),
      wait_rank(session.wait_reason),
      -session.last_seq_no,
      session.session_id
    }
  end

  defp health_rank("quarantined"), do: 0
  defp health_rank("degraded"), do: 1
  defp health_rank(_healthy), do: 2

  defp wait_rank("approval"), do: 0
  defp wait_rank("lease_recovery"), do: 1
  defp wait_rank("operator"), do: 2
  defp wait_rank("action"), do: 3
  defp wait_rank("timer"), do: 4
  defp wait_rank("external_dependency"), do: 5
  defp wait_rank(_none), do: 6
end
