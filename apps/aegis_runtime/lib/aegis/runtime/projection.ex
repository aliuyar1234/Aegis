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
    %{
      tenant_id: durable.tenant_id,
      workspace_id: durable.workspace_id,
      session_id: durable.session_id,
      phase: to_string(durable.phase),
      control_mode: to_string(durable.control_mode),
      health: to_string(durable.health),
      owner_node: durable.owner_node,
      lease_epoch: durable.lease_epoch,
      wait_reason: to_string(durable.wait_reason),
      last_seq_no: durable.last_seq_no,
      latest_checkpoint_id: durable.latest_checkpoint_id,
      deadlines: durable.deadlines,
      pending_approvals: durable.pending_approvals,
      in_flight_actions: in_flight_actions(durable.action_ledger),
      recent_artifacts: durable.recent_artifacts,
      fenced: durable.fenced,
      latest_recovery_reason: durable.latest_recovery_reason
    }
  end

  defp in_flight_actions(action_ledger) do
    action_ledger
    |> Enum.filter(&(&1.status not in ["succeeded", "failed", "cancelled"]))
    |> Enum.sort_by(& &1.action_id)
  end
end
