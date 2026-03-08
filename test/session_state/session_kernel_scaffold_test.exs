defmodule SessionKernelScaffoldTest do
  use ExUnit.Case, async: false

  alias Aegis.Runtime
  alias Aegis.Runtime.SessionState

  setup do
    session_id = "session-#{System.unique_integer([:positive])}"

    {:ok, tree_pid} =
      Runtime.start_session(%{
        session_id: session_id,
        tenant_id: "tenant-1",
        workspace_id: "workspace-1",
        requested_by: "test-suite",
        session_kind: "browser_operation"
      })

    on_exit(fn ->
      if Process.alive?(tree_pid) do
        Process.exit(tree_pid, :shutdown)
      end
    end)

    %{session_id: session_id, tree_pid: tree_pid}
  end

  test "current phase starts on session kernel" do
    assert File.read!("meta/current-phase.yaml") =~ "PHASE-01"
  end

  test "runtime model doc exists" do
    assert File.exists?("docs/design-docs/runtime-model.md")
  end

  test "bootstraps authoritative session state with durable and ephemeral sections", %{
    session_id: session_id
  } do
    state = Runtime.snapshot(session_id)

    assert %SessionState{} = state
    assert state.durable.phase == :provisioning
    assert state.durable.control_mode == :autonomous
    assert state.durable.health == :healthy
    assert state.durable.wait_reason == :none
    assert state.durable.last_seq_no == 2

    assert Enum.map(Runtime.events(session_id), & &1.type) == [
             "session.created",
             "checkpoint.created"
           ]

    refute Map.has_key?(Map.from_struct(state.durable), :recent_events)
    assert Map.has_key?(Map.from_struct(state.ephemeral), :recent_events)
    assert Runtime.projection(session_id).phase == "provisioning"
    assert Runtime.projection(session_id).owner_node == Atom.to_string(node())
  end

  test "supports the locked phase lifecycle transitions with explicit wait reasons", %{
    session_id: session_id
  } do
    assert {:ok, _} =
             Runtime.dispatch(
               session_id,
               {:hydrate, %{restored_from_checkpoint_id: "cp-001", lease_epoch: 1}}
             )

    assert {:ok, _} =
             Runtime.dispatch(
               session_id,
               {:activate, %{owner_node: "runtime@node", lease_epoch: 2}}
             )

    assert {:ok, _} =
             Runtime.dispatch(session_id, {:wait, :approval, %{detail: "awaiting human review"}})

    waiting_projection = Runtime.projection(session_id)
    assert waiting_projection.phase == "waiting"
    assert waiting_projection.wait_reason == "approval"

    assert {:ok, _} = Runtime.dispatch(session_id, {:resume, %{reason: "approval granted"}})
    assert Runtime.projection(session_id).phase == "active"

    assert {:ok, _} =
             Runtime.dispatch(session_id, {:cancel, %{reason: "operator requested stop"}})

    assert Runtime.snapshot(session_id).durable.phase == :cancelling

    assert {:ok, _} = Runtime.dispatch(session_id, {:complete, %{reason: "cancelled cleanly"}})

    final_state = Runtime.snapshot(session_id)
    assert final_state.durable.phase == :terminal
    assert final_state.durable.wait_reason == :none
  end

  test "rejects invalid wait reasons", %{session_id: session_id} do
    assert {:ok, _} =
             Runtime.dispatch(
               session_id,
               {:activate, %{owner_node: "runtime@node", lease_epoch: 1}}
             )

    assert {:error, {:invalid_wait_reason, :mystery}} =
             Runtime.dispatch(session_id, {:wait, :mystery, %{}})
  end

  test "starts the canonical per-session supervisor tree and registers child ownership boundaries",
       %{
         session_id: session_id,
         tree_pid: tree_pid
       } do
    state = await_registered_components(session_id)

    expected_child_ids =
      MapSet.new([
        Aegis.Runtime.SessionKernel,
        Aegis.Runtime.ParticipantBridge,
        Aegis.Runtime.TimerManager,
        Aegis.Runtime.CheckpointWorker,
        Aegis.Runtime.ToolRouter,
        Aegis.Runtime.PolicyCoordinator,
        Aegis.Runtime.ChildAgentSupervisor,
        Aegis.Runtime.EventFanout,
        Aegis.Runtime.ArtifactCoordinator
      ])

    child_ids =
      tree_pid
      |> Supervisor.which_children()
      |> Enum.map(fn {id, _pid, _type, _modules} -> id end)
      |> MapSet.new()

    assert child_ids == expected_child_ids

    assert Map.keys(state.ephemeral.component_pids) |> Enum.sort() == [
             :artifact_coordinator,
             :checkpoint_worker,
             :child_agent_supervisor,
             :event_fanout,
             :participant_bridge,
             :policy_coordinator,
             :timer_manager,
             :tool_router
           ]
  end

  test "emits in-memory events and stable projection updates for commands", %{
    session_id: session_id
  } do
    assert {:ok, _} =
             Runtime.dispatch(
               session_id,
               {:activate, %{owner_node: "runtime@node", lease_epoch: 3}}
             )

    assert {:ok, %{events: events}} =
             Runtime.dispatch(session_id, {
               :request_action,
               %{
                 action_id: "action-1",
                 tool_id: "browser.navigate",
                 tool_schema_version: "v1",
                 risk_class: "read_only",
                 idempotency_class: "idempotent",
                 timeout_class: "standard",
                 mutating: false
               }
             })

    assert List.last(events).type == "action.requested"

    assert {:ok, _} =
             Runtime.dispatch(session_id, {
               :request_approval,
               %{
                 approval_id: "approval-1",
                 action_id: "action-1",
                 action_hash: "hash-1",
                 expires_at: "2026-03-08T12:00:00Z",
                 risk_class: "high"
               }
             })

    assert {:ok, _} =
             Runtime.dispatch(session_id, {
               :register_artifact,
               %{
                 artifact_id: "artifact-1",
                 artifact_kind: "screenshot",
                 storage_ref: "s3://aegis-artifacts/artifact-1"
               }
             })

    assert {:ok, _} =
             Runtime.dispatch(
               session_id,
               {:change_control_mode, :supervised, %{reason: "operator shadowing"}}
             )

    projection = Runtime.projection(session_id)

    assert projection.control_mode == "supervised"
    assert [%{action_id: "action-1"}] = projection.in_flight_actions
    assert [%{approval_id: "approval-1"}] = projection.pending_approvals
    assert [%{artifact_id: "artifact-1"}] = projection.recent_artifacts
    assert projection.last_seq_no == 7

    event_types = Runtime.events(session_id) |> Enum.map(& &1.type)

    assert Enum.take(event_types, -4) == [
             "action.requested",
             "approval.requested",
             "artifact.registered",
             "session.mode_changed"
           ]
  end

  defp await_registered_components(session_id, attempts \\ 20)

  defp await_registered_components(session_id, attempts) when attempts > 0 do
    state = Runtime.snapshot(session_id)

    if map_size(state.ephemeral.component_pids) == 8 do
      state
    else
      Process.sleep(20)
      await_registered_components(session_id, attempts - 1)
    end
  end

  defp await_registered_components(session_id, 0), do: Runtime.snapshot(session_id)
end
