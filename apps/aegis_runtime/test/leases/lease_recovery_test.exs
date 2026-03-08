defmodule Aegis.Runtime.LeaseRecoveryTest do
  use ExUnit.Case, async: false

  alias Aegis.Repo
  alias Aegis.Runtime
  alias Ecto.Adapters.SQL

  setup do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(Aegis.Repo)
    Ecto.Adapters.SQL.Sandbox.mode(Aegis.Repo, {:shared, self()})
    Aegis.Events.reset!()

    session_id = "lease-session-#{System.unique_integer([:positive])}"
    owner_node = "node-a@runtime"

    {:ok, tree_pid} =
      Runtime.start_session(%{
        session_id: session_id,
        tenant_id: "tenant-lease",
        workspace_id: "workspace-lease",
        requested_by: "lease-suite",
        session_kind: "browser_operation",
        owner_node: owner_node
      })

    on_exit(fn ->
      if Process.alive?(tree_pid) do
        Process.exit(tree_pid, :shutdown)
      end
    end)

    %{session_id: session_id, owner_node: owner_node}
  end

  test "claims an authoritative lease row and renews it on accepted commands", %{
    session_id: session_id,
    owner_node: owner_node
  } do
    assert {:ok, lease} = Runtime.lease(session_id)
    assert lease.owner_node == owner_node
    assert lease.lease_epoch == 1
    assert lease.lease_status == :active
    assert count_rows("session_leases") == 1

    force_short_expiry(session_id)
    assert {:ok, before_dispatch} = Runtime.lease(session_id)

    assert {:ok, %{lease: renewed_lease}} =
             Runtime.dispatch(
               session_id,
               {:activate, %{}},
               owner_node: owner_node,
               lease_epoch: 1
             )

    assert renewed_lease.lease_status == :active
    assert DateTime.compare(renewed_lease.lease_expires_at, before_dispatch.lease_expires_at) == :gt
    assert Runtime.projection(session_id).phase == "active"
  end

  test "rejects stale lease epochs and wrong owners", %{session_id: session_id, owner_node: owner_node} do
    assert {:error, {:stale_lease_epoch, 0, 1}} =
             Runtime.dispatch(
               session_id,
               {:activate, %{}},
               owner_node: owner_node,
               lease_epoch: 0
             )

    assert {:error, {:lease_owner_mismatch, "node-b@runtime", lease}} =
             Runtime.dispatch(
               session_id,
               {:activate, %{}},
               owner_node: "node-b@runtime",
               lease_epoch: 1
             )

    assert lease.owner_node == owner_node
    assert Runtime.projection(session_id).phase == "provisioning"
    assert Enum.map(Runtime.events(session_id), & &1.type) == ["session.created", "checkpoint.created"]
  end

  test "self-fences on lease ambiguity and preserves fenced state in replay", %{
    session_id: session_id,
    owner_node: owner_node
  } do
    assert {:ok, _} =
             Runtime.dispatch(
               session_id,
               {:activate, %{}},
               owner_node: owner_node,
               lease_epoch: 1
             )

    assert {:ok, %{projection: projection, events: events, lease: lease}} =
             Runtime.report_lease_ambiguity(session_id, %{reason: "db_partition"})

    assert projection.phase == "waiting"
    assert projection.wait_reason == "lease_recovery"
    assert projection.health == "degraded"
    assert projection.fenced
    assert lease.lease_status == :ambiguous
    assert Enum.take(Enum.map(events, & &1.type), -4) == [
             "system.lease_lost",
             "health.degraded",
             "session.waiting",
             "checkpoint.created"
           ]

    assert {:error, {:lease_not_authoritative, :ambiguous, _lease}} =
             Runtime.dispatch(
               session_id,
               {:request_action, %{action_id: "action-1", tool_id: "browser.navigate"}},
               owner_node: owner_node,
               lease_epoch: 1
             )

    assert {:ok, replay} = Runtime.historical_replay(session_id)
    assert replay.replay_state.phase == "waiting"
    assert replay.replay_state.wait_reason == "lease_recovery"
    assert replay.replay_state.health == "degraded"
    assert replay.replay_state.fenced
    assert replay.replay_state.latest_recovery_reason == "db_partition"
  end

  test "adopts after lease expiry and resumes with a higher epoch", %{
    session_id: session_id,
    owner_node: owner_node
  } do
    assert {:ok, _} =
             Runtime.dispatch(
               session_id,
               {:activate, %{}},
               owner_node: owner_node,
               lease_epoch: 1
             )

    force_expiry(session_id)

    restored_from_checkpoint_id = Runtime.snapshot(session_id).durable.latest_checkpoint_id

    assert {:ok, %{projection: projection, events: events, lease: lease}} =
             Runtime.adopt(session_id, %{
               owner_node: "node-b@runtime",
               restored_from_checkpoint_id: restored_from_checkpoint_id,
               recovery_reason: "node_loss"
             })

    assert lease.owner_node == "node-b@runtime"
    assert lease.lease_epoch == 2
    assert lease.lease_status == :active
    assert projection.phase == "active"
    assert projection.wait_reason == "none"
    assert projection.health == "healthy"
    refute projection.fenced
    assert Enum.take(Enum.map(events, & &1.type), -4) == [
             "session.hydrated",
             "session.owned",
             "system.node_recovered",
             "checkpoint.created"
           ]

    assert {:error, {:lease_owner_mismatch, ^owner_node, _lease}} =
             Runtime.dispatch(
               session_id,
               {:change_control_mode, :supervised, %{reason: "stale owner"}},
               owner_node: owner_node,
               lease_epoch: 1
             )

    assert {:ok, replay} = Runtime.historical_replay(session_id)
    assert replay.replay_state.owner_node == "node-b@runtime"
    assert replay.replay_state.lease_epoch == 2
    assert replay.replay_state.health == "healthy"
    refute replay.replay_state.fenced
    assert replay.replay_state.latest_recovery_reason == "node_loss"
  end

  defp force_short_expiry(session_id) do
    SQL.query!(
      Repo,
      """
      UPDATE session_leases
      SET lease_expires_at = NOW() + INTERVAL '1 second',
          updated_at = NOW()
      WHERE session_id = $1
      """,
      [session_id]
    )
  end

  defp force_expiry(session_id) do
    SQL.query!(
      Repo,
      """
      UPDATE session_leases
      SET lease_expires_at = NOW() - INTERVAL '1 second',
          updated_at = NOW()
      WHERE session_id = $1
      """,
      [session_id]
    )
  end

  defp count_rows(table) do
    SQL.query!(Repo, "SELECT COUNT(*) FROM #{table}", []).rows
    |> List.first()
    |> List.first()
  end
end
