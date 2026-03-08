defmodule Aegis.Runtime.Projection do
  @moduledoc """
  Stable operator-facing projection builder for Phase 01.

  This projection mirrors the fields locked in:
  - `docs/design-docs/projection-model.md`
  - `schema/jsonschema/operator-session-view.schema.json`

  The projection is derived from authoritative session state and must not become a
  second hidden source of truth.
  """

  alias Aegis.Runtime.SessionState

  @spec from_state(SessionState.t()) :: map()
  def from_state(%SessionState{durable: durable}) do
    from_snapshot(durable)
  end

  @spec from_snapshot(map()) :: map()
  def from_snapshot(durable) when is_map(durable) do
    %{
      tenant_id: Map.fetch!(durable, :tenant_id),
      workspace_id: Map.fetch!(durable, :workspace_id),
      isolation_tier: Map.get(durable, :isolation_tier, "tier_a"),
      session_id: Map.fetch!(durable, :session_id),
      phase: durable |> Map.fetch!(:phase) |> to_string(),
      control_mode: durable |> Map.fetch!(:control_mode) |> to_string(),
      health: durable |> Map.fetch!(:health) |> to_string(),
      owner_node: Map.fetch!(durable, :owner_node),
      lease_epoch: Map.fetch!(durable, :lease_epoch),
      wait_reason: durable |> Map.fetch!(:wait_reason) |> to_string(),
      last_seq_no: Map.fetch!(durable, :last_seq_no),
      latest_checkpoint_id: Map.get(durable, :latest_checkpoint_id),
      deadlines: Map.get(durable, :deadlines, []),
      pending_approvals: Map.get(durable, :pending_approvals, []),
      in_flight_actions: durable |> Map.get(:action_ledger, []) |> in_flight_actions(),
      recent_artifacts: Map.get(durable, :recent_artifacts, []),
      fenced: Map.get(durable, :fenced, false),
      latest_recovery_reason: Map.get(durable, :latest_recovery_reason)
    }
  end

  defp in_flight_actions(action_ledger) do
    action_ledger
    |> Enum.filter(&(&1.status not in ["succeeded", "failed", "cancelled", "uncertain", "denied", "approval_expired"]))
    |> Enum.sort_by(& &1.action_id)
  end
end
