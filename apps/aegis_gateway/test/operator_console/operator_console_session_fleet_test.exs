defmodule OperatorConsoleSessionFleetTest do
  use ExUnit.Case, async: false

  alias Aegis.Events
  alias Aegis.ExecutionBridge
  alias Aegis.Gateway.OperatorConsole
  alias Aegis.Runtime

  setup do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(Aegis.Repo)
    Ecto.Adapters.SQL.Sandbox.mode(Aegis.Repo, {:shared, self()})

    Events.reset!()
    ExecutionBridge.reset!()

    :ok
  end

  test "lists stable operator session views and supports bounded fleet filters" do
    approval_session_id =
      start_session!(%{
        session_id: unique_session_id("approval"),
        tenant_id: "tenant-ops",
        workspace_id: "workspace-ops"
      })

    active_session_id =
      start_session!(%{
        session_id: unique_session_id("active"),
        tenant_id: "tenant-ops",
        workspace_id: "workspace-ops"
      })

    degraded_session_id =
      start_session!(%{
        session_id: unique_session_id("degraded"),
        tenant_id: "tenant-risk",
        workspace_id: "workspace-risk"
      })

    quarantined_session_id =
      start_session!(%{
        session_id: unique_session_id("quarantined"),
        tenant_id: "tenant-risk",
        workspace_id: "workspace-risk"
      })

    activate!(approval_session_id)
    request_action!(approval_session_id, "action-approval-1")
    request_approval!(approval_session_id, "action-approval-1", "approval-1")

    dispatch!(
      approval_session_id,
      {:wait, :approval, %{detail: "awaiting operator", blocking_approval_id: "approval-1"}}
    )

    dispatch!(
      approval_session_id,
      {:change_control_mode, :supervised, %{reason: "operator watching"}}
    )

    dispatch!(
      approval_session_id,
      {:register_artifact,
       %{
         artifact_id: "artifact-approval-1",
         artifact_kind: "screenshot",
         storage_ref: "s3://aegis/approval-1"
       }}
    )

    activate!(active_session_id)

    activate!(degraded_session_id)

    assert {:ok, _result} =
             Runtime.report_lease_ambiguity(degraded_session_id, %{reason: "lease_contested"})

    activate!(quarantined_session_id)
    dispatch!(quarantined_session_id, {:quarantine, %{reason: "operator_hold"}})

    fleet = OperatorConsole.session_fleet()
    session_ids = Enum.map(fleet.sessions, & &1.session_id)

    assert Enum.sort(session_ids) ==
             Enum.sort([
               approval_session_id,
               active_session_id,
               degraded_session_id,
               quarantined_session_id
             ])

    approval_view = find_session!(fleet.sessions, approval_session_id)
    assert approval_view.phase == "waiting"
    assert approval_view.control_mode == "supervised"
    assert approval_view.wait_reason == "approval"
    assert [%{approval_id: "approval-1"}] = approval_view.pending_approvals
    assert [%{action_id: "action-approval-1"}] = approval_view.in_flight_actions
    assert [%{artifact_id: "artifact-approval-1"}] = approval_view.recent_artifacts

    degraded_view = find_session!(fleet.sessions, degraded_session_id)
    assert degraded_view.health == "degraded"
    assert degraded_view.fenced
    assert degraded_view.wait_reason == "lease_recovery"
    assert degraded_view.latest_recovery_reason == "lease_contested"

    assert Enum.map(OperatorConsole.session_fleet(health: "degraded").sessions, & &1.session_id) ==
             [degraded_session_id]

    assert Enum.map(
             OperatorConsole.session_fleet(
               tenant_id: "tenant-ops",
               has_pending_approval: true,
               wait_reason: "approval"
             ).sessions,
             & &1.session_id
           ) == [approval_session_id]

    assert Enum.map(
             OperatorConsole.session_fleet(
               query: "workspace-risk",
               session_ids: [degraded_session_id]
             ).sessions,
             & &1.session_id
           ) == [degraded_session_id]

    assert has_runbook?(fleet.runbooks, "docs/runbooks/degraded-system-mode.md")
    assert has_runbook?(fleet.runbooks, "docs/runbooks/transport-lag.md")

    assert fleet.system_health.status == "quarantined"
    assert fleet.system_health.sessions.total == 4
    assert fleet.system_health.sessions.by_health["healthy"] == 2
    assert fleet.system_health.sessions.by_health["degraded"] == 1
    assert fleet.system_health.sessions.by_health["quarantined"] == 1
  end

  test "exposes single-session views and rolls up worker fleet health" do
    session_id =
      start_session!(%{
        session_id: unique_session_id("worker-health"),
        tenant_id: "tenant-console",
        workspace_id: "workspace-console"
      })

    activate!(session_id)

    assert {:ok, _registration} =
             ExecutionBridge.register_worker(%{
               worker_id: "worker-browser-1",
               worker_kind: "browser",
               worker_version: "0.5.0",
               supported_contract_versions: ["v1"],
               advertised_capacity: 4,
               available_capacity: 3,
               attributes: %{"region" => "eu-central"}
             })

    assert {:ok, _registration} =
             ExecutionBridge.register_worker(%{
               worker_id: "worker-planner-1",
               worker_kind: "planner",
               worker_version: "0.5.0",
               supported_contract_versions: ["v1"],
               advertised_capacity: 2,
               available_capacity: 0,
               status: "degraded",
               attributes: %{"region" => "eu-central"}
             })

    assert {:ok, view} = OperatorConsole.session_view(session_id)
    assert view.session_id == session_id
    assert view.phase == "active"
    assert view.health == "healthy"
    assert Map.has_key?(view, :owner_node)
    assert Map.has_key?(view, :lease_epoch)

    overview = OperatorConsole.system_health_overview()

    assert overview.status == "degraded"
    assert overview.sessions.total == 1
    assert overview.sessions.by_phase["active"] == 1
    assert overview.workers.total == 2
    assert overview.workers.by_kind["browser"] == 1
    assert overview.workers.by_kind["planner"] == 1
    assert overview.workers.by_status["active"] == 1
    assert overview.workers.by_status["degraded"] == 1
    assert overview.workers.advertised_capacity == 6
    assert overview.workers.available_capacity == 3
    assert has_runbook?(overview.runbooks, "docs/runbooks/degraded-system-mode.md")
  end

  test "builds session detail from replay state and checkpoint metadata" do
    session_id =
      start_session!(%{
        session_id: unique_session_id("detail"),
        tenant_id: "tenant-detail",
        workspace_id: "workspace-detail"
      })

    activate!(session_id)
    request_action!(session_id, "action-detail-1")
    request_approval!(session_id, "action-detail-1", "approval-detail-1")

    dispatch!(
      session_id,
      {:wait, :approval,
       %{detail: "waiting for human review", blocking_approval_id: "approval-detail-1"}}
    )

    dispatch!(
      session_id,
      {:register_artifact,
       %{
         artifact_id: "artifact-detail-1",
         artifact_kind: "dom_snapshot",
         storage_ref: "s3://aegis/detail-1",
         content_type: "application/json",
         size_bytes: 512,
         action_id: "action-detail-1",
         recorded_at: "2026-03-08T13:20:00Z"
       }}
    )

    assert {:ok, detail} = OperatorConsole.session_detail(session_id)

    assert detail.session.session_id == session_id
    assert detail.session.phase == "waiting"
    assert detail.current_state.session_kind == "browser_operation"
    assert detail.current_state.requested_by == "operator-console-test"
    assert detail.current_state.wait_reason == "approval"
    assert detail.current_state.latest_checkpoint_id == detail.session.latest_checkpoint_id
    assert [%{approval_id: "approval-detail-1"}] = detail.approvals
    assert [%{action_id: "action-detail-1"}] = detail.in_flight_actions

    assert [%{artifact_id: "artifact-detail-1", storage_ref: "s3://aegis/detail-1"}] =
             detail.artifacts

    assert detail.controls.pause
    assert detail.controls.abort
    assert detail.controls.take_control
    assert has_runbook?(detail.runbooks, "docs/runbooks/approval-timeout.md")
    assert has_runbook?(detail.runbooks, "docs/runbooks/artifact-store-outage.md")

    assert detail.latest_checkpoint != nil
    assert detail.latest_checkpoint.phase == "waiting"

    assert Enum.any?(
             detail.checkpoints,
             &(&1.checkpoint_id == detail.latest_checkpoint.checkpoint_id)
           )
  end

  test "exposes replay timeline, checkpoint markers, and scrubbed historical state" do
    session_id =
      start_session!(%{
        session_id: unique_session_id("replay"),
        tenant_id: "tenant-replay",
        workspace_id: "workspace-replay"
      })

    activate!(session_id)
    request_action!(session_id, "action-replay-1")
    request_approval!(session_id, "action-replay-1", "approval-replay-1")

    dispatch!(
      session_id,
      {:wait, :approval,
       %{detail: "waiting for approval", blocking_approval_id: "approval-replay-1"}}
    )

    dispatch!(
      session_id,
      {:change_control_mode, :supervised, %{reason: "operator shadow"}}
    )

    dispatch!(
      session_id,
      {:register_artifact,
       %{
         artifact_id: "artifact-replay-1",
         artifact_kind: "screenshot",
         storage_ref: "s3://aegis/replay-1",
         sha256: "sha256-replay-1",
         content_type: "image/png",
         size_bytes: 1024,
         action_id: "action-replay-1",
         recorded_at: "2026-03-08T13:25:00Z"
       }}
    )

    waiting_event =
      Events.events(session_id)
      |> Enum.find(&(&1.type == "session.waiting"))

    assert {:ok, replay_now} = OperatorConsole.session_replay(session_id)
    assert replay_now.selected_state.control_mode == "supervised"
    assert Enum.any?(replay_now.timeline, &(&1.entry_kind == "checkpoint"))

    assert Enum.any?(
             replay_now.timeline,
             &(&1.type == "approval.requested" and "approval" in &1.overlay_tags)
           )

    assert Enum.any?(
             replay_now.timeline,
             &(&1.type == "artifact.registered" and "artifact" in &1.overlay_tags)
           )

    assert has_runbook?(replay_now.runbooks, "docs/runbooks/event-corruption-quarantine.md")
    assert has_runbook?(replay_now.runbooks, "docs/runbooks/duplicate-execution.md")

    assert {:ok, replay_at_wait} =
             OperatorConsole.session_replay(session_id, seq_no: waiting_event.seq_no)

    assert replay_at_wait.scrubber.selected_seq_no == waiting_event.seq_no
    assert replay_at_wait.selected_state.phase == "waiting"
    assert replay_at_wait.selected_state.control_mode == "autonomous"
    assert replay_at_wait.selected_state.recent_artifacts == []

    assert {:ok, artifact} = OperatorConsole.artifact_view(session_id, "artifact-replay-1")
    assert artifact.storage_ref == "s3://aegis/replay-1"
    assert artifact.action_id == "action-replay-1"
    assert artifact.registered_seq_no > waiting_event.seq_no
    assert artifact.content_type == "image/png"
  end

  test "records operator intervention flows as durable runtime events" do
    session_id =
      start_session!(%{
        session_id: unique_session_id("operator"),
        tenant_id: "tenant-operator",
        workspace_id: "workspace-operator"
      })

    activate!(session_id)

    assert {:ok, _result} = OperatorConsole.operator_join(session_id, "operator-1")

    assert {:ok, _result} =
             OperatorConsole.add_operator_note(
               session_id,
               "operator-1",
               "note-1",
               "Need manual review"
             )

    assert {:ok, _result} =
             OperatorConsole.pause_session(session_id, "operator-1", "manual_review")

    assert {:ok, paused_detail} = OperatorConsole.session_detail(session_id)
    assert paused_detail.current_state.phase == "waiting"
    assert paused_detail.current_state.control_mode == "paused"
    assert paused_detail.current_state.wait_reason == "operator"
    assert paused_detail.controls.return_control

    assert [
             %{
               note_ref: "note-1",
               operator_id: "operator-1",
               note_text: "Need manual review"
             }
           ] = paused_detail.summary_capsule.operator_notes

    assert has_runbook?(paused_detail.runbooks, "docs/runbooks/operator-intervention.md")

    fleet = OperatorConsole.session_fleet(wait_reason: "operator")
    assert Enum.map(fleet.sessions, & &1.session_id) == [session_id]
    assert has_runbook?(fleet.runbooks, "docs/runbooks/degraded-system-mode.md")

    initial_operator_events =
      session_id
      |> Events.events()
      |> Enum.filter(&String.starts_with?(&1.type, "operator."))

    assert Enum.map(initial_operator_events, & &1.type) == [
             "operator.joined",
             "operator.note_added",
             "operator.paused"
           ]

    assert Enum.all?(initial_operator_events, &(&1.actor_kind == "operator"))
    assert Enum.all?(initial_operator_events, &(&1.actor_id == "operator-1"))

    assert Enum.find(initial_operator_events, &(&1.type == "operator.note_added")).payload.note_text ==
             "Need manual review"

    assert {:ok, _result} =
             OperatorConsole.return_control(
               session_id,
               "operator-1",
               "pause_review_complete",
               :supervised
             )

    assert {:ok, supervised_detail} = OperatorConsole.session_detail(session_id)
    assert supervised_detail.current_state.phase == "active"
    assert supervised_detail.current_state.control_mode == "supervised"
    assert supervised_detail.current_state.latest_recovery_reason == "pause_review_complete"

    assert {:ok, _result} =
             OperatorConsole.take_control(session_id, "operator-1", "manual_takeover")

    assert {:ok, takeover_detail} = OperatorConsole.session_detail(session_id)
    assert takeover_detail.current_state.phase == "waiting"
    assert takeover_detail.current_state.control_mode == "human_control"
    assert takeover_detail.current_state.wait_reason == "operator"

    assert {:ok, _result} =
             OperatorConsole.return_control(
               session_id,
               "operator-1",
               "takeover_complete",
               :autonomous
             )

    assert {:ok, autonomous_detail} = OperatorConsole.session_detail(session_id)
    assert autonomous_detail.current_state.phase == "active"
    assert autonomous_detail.current_state.control_mode == "autonomous"
    assert autonomous_detail.current_state.latest_recovery_reason == "takeover_complete"

    assert {:ok, _result} =
             OperatorConsole.abort_session(session_id, "operator-1", "manual_abort")

    assert {:ok, cancelling_detail} = OperatorConsole.session_detail(session_id)
    assert cancelling_detail.current_state.phase == "cancelling"
    assert cancelling_detail.current_state.wait_reason == "none"
    assert has_runbook?(cancelling_detail.runbooks, "docs/runbooks/operator-intervention.md")

    operator_events =
      session_id
      |> Events.events()
      |> Enum.filter(&String.starts_with?(&1.type, "operator."))

    assert Enum.map(operator_events, & &1.type) == [
             "operator.joined",
             "operator.note_added",
             "operator.paused",
             "operator.returned_control",
             "operator.took_control",
             "operator.returned_control",
             "operator.abort_requested"
           ]

    assert Enum.all?(operator_events, &(&1.actor_kind == "operator"))
    assert Enum.all?(operator_events, &(&1.actor_id == "operator-1"))

    assert {:ok, replay} = OperatorConsole.session_replay(session_id)

    assert Enum.any?(
             replay.timeline,
             &(&1.type == "operator.note_added" and "operator" in &1.overlay_tags)
           )

    assert Enum.any?(
             replay.timeline,
             &(&1.type == "operator.abort_requested" and "operator" in &1.overlay_tags)
           )

    assert Enum.any?(
             replay.timeline,
             &(&1.type == "operator.took_control" and
                 &1.headline == "Operator took control: operator-1")
           )
  end

  test "lets operators grant and deny approval-bound actions through the gateway" do
    grant_session_id =
      start_session!(%{
        session_id: unique_session_id("approval-grant"),
        tenant_id: "tenant-approval-grant",
        workspace_id: "workspace-approval-grant"
      })

    activate!(grant_session_id)
    request_submit_action!(grant_session_id, "action-submit-grant-1")

    assert {:ok, grant_detail} = OperatorConsole.session_detail(grant_session_id)
    assert grant_detail.current_state.phase == "waiting"
    assert grant_detail.controls.grant_approval
    assert grant_detail.controls.deny_approval

    [%{approval_id: approval_id, action_hash: action_hash}] = grant_detail.approvals

    assert {:ok, _result} =
             OperatorConsole.grant_approval(
               grant_session_id,
               "operator-approval-1",
               approval_id,
               action_hash
             )

    assert {:ok, granted_detail} = OperatorConsole.session_detail(grant_session_id)
    assert granted_detail.approvals == []
    assert granted_detail.current_state.phase == "active"

    assert {:ok, granted_replay} = OperatorConsole.session_replay(grant_session_id)

    assert Enum.any?(
             granted_replay.timeline,
             &(&1.type == "approval.granted" and &1.headline == "Approval granted for action-submit-grant-1")
           )

    deny_session_id =
      start_session!(%{
        session_id: unique_session_id("approval-deny"),
        tenant_id: "tenant-approval-deny",
        workspace_id: "workspace-approval-deny"
      })

    activate!(deny_session_id)
    request_submit_action!(deny_session_id, "action-submit-deny-1")

    assert {:ok, deny_detail} = OperatorConsole.session_detail(deny_session_id)
    [%{approval_id: deny_approval_id, action_hash: deny_action_hash}] = deny_detail.approvals

    assert {:ok, _result} =
             OperatorConsole.deny_approval(
               deny_session_id,
               "operator-approval-2",
               deny_approval_id,
               deny_action_hash,
               "manual_rejection"
             )

    assert {:ok, denied_detail} = OperatorConsole.session_detail(deny_session_id)
    assert denied_detail.approvals == []
    assert denied_detail.current_state.phase == "active"
    assert denied_detail.in_flight_actions == []

    assert {:ok, denied_replay} = OperatorConsole.session_replay(deny_session_id)

    assert Enum.any?(
             denied_replay.timeline,
             &(&1.type == "approval.denied" and &1.headline == "Approval denied for action-submit-deny-1")
           )
  end

  defp start_session!(attrs) do
    session_id = Map.fetch!(attrs, :session_id)

    {:ok, tree_pid} =
      Runtime.start_session(
        Map.merge(
          %{
            requested_by: "operator-console-test",
            session_kind: "browser_operation"
          },
          attrs
        )
      )

    on_exit(fn ->
      if Process.alive?(tree_pid) do
        Process.exit(tree_pid, :shutdown)
      end
    end)

    session_id
  end

  defp activate!(session_id) do
    {:ok, lease} = Runtime.lease(session_id)

    dispatch!(
      session_id,
      {:activate, %{owner_node: lease.owner_node, lease_epoch: lease.lease_epoch}}
    )
  end

  defp request_action!(session_id, action_id) do
    dispatch!(
      session_id,
      {:request_action,
       %{
         action_id: action_id,
         tool_id: "browser.navigate",
         tool_schema_version: "v1",
         worker_kind: "browser",
         input: %{url: "https://example.com"},
         risk_class: "read_only",
         idempotency_class: "idempotent",
         timeout_class: "short",
         mutating: false
       }}
    )
  end

  defp request_approval!(session_id, action_id, approval_id) do
    dispatch!(
      session_id,
      {:request_approval,
       %{
         approval_id: approval_id,
         action_id: action_id,
         action_hash: "hash-#{approval_id}",
         expires_at: "2026-03-08T12:30:00Z",
         risk_class: "high"
       }}
    )
  end

  defp request_submit_action!(session_id, action_id) do
    dispatch!(
      session_id,
      {:request_action,
       %{
         action_id: action_id,
         tool_id: "browser.submit",
         tool_schema_version: "v1",
         worker_kind: "browser",
         input: %{selector: "form#profile"}
       }}
    )
  end

  defp dispatch!(session_id, command) do
    {:ok, lease} = Runtime.lease(session_id)

    assert {:ok, _result} =
             Runtime.dispatch(
               session_id,
               command,
               owner_node: lease.owner_node,
               lease_epoch: lease.lease_epoch
             )
  end

  defp find_session!(sessions, session_id) do
    Enum.find(sessions, &(&1.session_id == session_id)) ||
      flunk("expected session #{session_id} in fleet")
  end

  defp has_runbook?(runbooks, path) do
    Enum.any?(runbooks, &(&1.path == path))
  end

  defp unique_session_id(prefix) do
    "#{prefix}-#{System.unique_integer([:positive])}"
  end
end
