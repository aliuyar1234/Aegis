defmodule Aegis.Events.ReplayTest do
  use ExUnit.Case, async: false

  alias Aegis.Events
  alias Aegis.Repo
  alias Ecto.Adapters.SQL

  @repo_root Path.expand("../../../..", __DIR__)
  @fixture_path Path.join(@repo_root, "test/replay/fixtures/golden_timeline_example.exs")

  setup do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(Aegis.Repo)
    Ecto.Adapters.SQL.Sandbox.mode(Aegis.Repo, {:shared, self()})
    Events.reset!()
    :ok
  end

  test "stores append batches atomically with seq_no, hash chain, outbox, and checkpoint rows" do
    session = fixture().session_state
    events = fixture().raw_events

    assert {:ok, result} = Events.append(session, events)

    assert length(result.persisted_events) == 3

    assert Enum.map(result.persisted_events, & &1.type) == [
             "session.created",
             "session.owned",
             "checkpoint.created"
           ]

    [created, owned, checkpoint_created] = result.persisted_events
    assert created.seq_no == 1
    assert owned.seq_no == 2
    assert checkpoint_created.seq_no == 3
    assert owned.prev_event_hash == created.event_hash
    assert checkpoint_created.prev_event_hash == owned.event_hash
    assert result.last_seq_no == 3
    assert result.checkpoint.checkpoint_id == "ckp-session-replay-3"
    assert result.checkpoint.tenant_id == session.tenant_id
    assert result.checkpoint.workspace_id == session.workspace_id
    assert length(result.outbox_entries) == 3
    assert Enum.all?(result.outbox_entries, &(&1.status == "pending"))
    assert Enum.all?(result.outbox_entries, &(&1.tenant_id == session.tenant_id))
    assert Enum.all?(result.outbox_entries, &(&1.workspace_id == session.workspace_id))

    assert count_rows("sessions") == 1
    assert count_rows("session_events") == 3
    assert count_rows("session_checkpoints") == 1
    assert count_rows("outbox") == 3
  end

  test "hydrates from latest checkpoint plus tail events" do
    fixture = fixture()
    session = fixture.session_state

    {:ok, _} =
      Events.append(session, fixture.raw_events)

    {:ok, _} =
      Events.append(
        session
        |> Map.put(:phase, "waiting")
        |> Map.put(:wait_reason, "approval"),
        [
          %{
            seq_no: 4,
            type: "session.waiting",
            payload: %{reason: "approval", detail: "awaiting approval"},
            recorded_at: ~U[2026-03-08 10:01:00Z]
          }
        ]
      )

    assert {:ok, hydrated} = Events.hydrate(session.session_id)
    assert hydrated.checkpoint.checkpoint_id == "ckp-session-replay-5"
    assert hydrated.replay_state.phase == "waiting"
    assert hydrated.replay_state.wait_reason == "approval"
    assert hydrated.replay_state.last_seq_no == 5
    assert Enum.map(hydrated.tail_events, & &1.type) == []
    assert hydrated.restored_event.type == "checkpoint.restored"
  end

  test "historical replay rebuilds operator-facing truth without external re-execution" do
    fixture = fixture()
    session = fixture.session_state

    {:ok, _} = Events.append(session, fixture.raw_events)

    {:ok, _} =
      Events.append(
        Map.merge(session, %{
          phase: "waiting",
          action_ledger: [
            %{
              action_id: "action-open-browser",
              tool_id: "browser.open",
              status: "requested",
              risk_class: "read_only",
              execution_id: nil,
              uncertain_side_effect: false,
              accept_deadline: nil,
              soft_deadline: nil,
              hard_deadline: nil
            }
          ],
          pending_approvals: [
            %{
              approval_id: "approval-open-browser",
              action_id: "action-open-browser",
              action_hash: "hash-open-browser",
              status: "pending",
              risk_class: "high",
              expires_at: "2026-03-08T11:00:00Z",
              decided_by: nil
            }
          ],
          artifact_ids: ["artifact-browser-screenshot"]
        }),
        [
          %{
            seq_no: 4,
            type: "action.requested",
            payload: %{
              action_id: "action-open-browser",
              tool_id: "browser.open",
              tool_schema_version: "v1",
              risk_class: "read_only",
              idempotency_class: "idempotent",
              timeout_class: "standard",
              mutating: false
            },
            recorded_at: ~U[2026-03-08 10:02:00Z]
          },
          %{
            seq_no: 5,
            type: "approval.requested",
            payload: %{
              approval_id: "approval-open-browser",
              action_id: "action-open-browser",
              action_hash: "hash-open-browser",
              expires_at: "2026-03-08T11:00:00Z",
              risk_class: "high",
              lease_epoch: 1
            },
            recorded_at: ~U[2026-03-08 10:03:00Z]
          },
          %{
            seq_no: 6,
            type: "artifact.registered",
            payload: %{
              artifact_id: "artifact-browser-screenshot",
              artifact_kind: "screenshot",
              sha256: "artifact-sha",
              content_type: "image/png",
              size_bytes: 1024,
              retention_class: "standard",
              redaction_state: "not_requested",
              storage_ref: "s3://aegis-artifacts/artifact-browser-screenshot",
              recorded_at: "2026-03-08T10:04:00Z",
              action_id: "action-open-browser"
            },
            recorded_at: ~U[2026-03-08 10:04:00Z]
          }
        ],
        checkpoint: false
      )

    assert {:ok, replay} = Events.historical_replay(session.session_id)
    assert Enum.any?(replay.timeline, &(&1.type == "artifact.registered"))
    assert replay.replay_state.last_seq_no == 6
    assert [%{action_id: "action-open-browser"}] = replay.replay_state.action_ledger
    assert [%{approval_id: "approval-open-browser"}] = replay.replay_state.pending_approvals
    assert [%{artifact_id: "artifact-browser-screenshot"}] = replay.replay_state.recent_artifacts
  end

  test "quarantines corrupted replay state instead of replaying a broken hash chain" do
    fixture = fixture()
    session = fixture.session_state

    {:ok, _} = Events.append(session, fixture.raw_events)

    SQL.query!(
      Repo,
      """
      UPDATE session_events
      SET prev_event_hash = 'corrupted-prev-hash'
      WHERE session_id = $1 AND seq_no = 2
      """,
      [session.session_id]
    )

    assert {:ok, replay} = Events.historical_replay(session.session_id)
    assert replay.replay_state.health == "quarantined"
    assert replay.replay_state.phase == "waiting"
    assert replay.replay_state.wait_reason == "external_dependency"
    assert replay.replay_state.fenced
    assert replay.replay_state.latest_recovery_reason == "event_corruption:hash_chain_mismatch"
    assert replay.integrity_failure.kind == "event_corruption"
    assert replay.integrity_failure.code == "hash_chain_mismatch"

    assert {:ok, hydrated} = Events.hydrate(session.session_id)
    assert hydrated.replay_state.health == "quarantined"
    assert hydrated.restored_event == nil
    assert hydrated.integrity_failure.code == "hash_chain_mismatch"
  end

  test "scopes replay, checkpoint, and outbox reads by tenant and workspace" do
    fixture = fixture()
    session = fixture.session_state

    {:ok, _} = Events.append(session, fixture.raw_events)

    scope = %{tenant_id: session.tenant_id, workspace_id: session.workspace_id}

    assert [%Aegis.Events.Checkpoint{} = checkpoint] = Events.checkpoints(session.session_id, scope)
    assert checkpoint.tenant_id == session.tenant_id
    assert checkpoint.workspace_id == session.workspace_id

    assert [_ | _] = Events.outbox(session.session_id, scope)
    assert [_ | _] = Events.events(session.session_id, scope)
    assert {:ok, replay} = Events.historical_replay(session.session_id, scope)
    assert replay.replay_state.session_id == session.session_id

    wrong_scope = %{tenant_id: "tenant-other", workspace_id: session.workspace_id}
    assert [] == Events.events(session.session_id, wrong_scope)
    assert [] == Events.checkpoints(session.session_id, wrong_scope)
    assert [] == Events.outbox(session.session_id, wrong_scope)
    assert {:error, :unknown_session} = Events.historical_replay(session.session_id, wrong_scope)
  end

  test "persists isolation tier across session rows, created events, and replay state" do
    fixture = fixture()
    session = Map.put(fixture.session_state, :isolation_tier, "tier_b")

    raw_events =
      Enum.map(fixture.raw_events, fn
        %{type: "session.created", payload: payload} = event ->
          %{event | payload: Map.put(payload, :isolation_tier, "tier_b")}

        event ->
          event
      end)

    assert {:ok, _result} = Events.append(session, raw_events)

    [session_row] = Events.sessions(%{tenant_id: session.tenant_id, workspace_id: session.workspace_id})
    assert session_row.isolation_tier == "tier_b"

    [created_event | _rest] = Events.events(session.session_id)
    assert created_event.payload.isolation_tier == "tier_b"

    assert {:ok, hydrated} = Events.hydrate(session.session_id)
    assert hydrated.replay_state.isolation_tier == "tier_b"
  end

  test "sql migration artifact defines the canonical phase 02 tables" do
    migration =
      Path.join(
        @repo_root,
        "apps/aegis_events/priv/postgres/migrations/202603080001_phase_02_core.sql"
      )
      |> File.read!()

    assert migration =~ "CREATE TABLE IF NOT EXISTS sessions"
    assert migration =~ "CREATE TABLE IF NOT EXISTS session_events"
    assert migration =~ "CREATE TABLE IF NOT EXISTS session_checkpoints"
    assert migration =~ "CREATE TABLE IF NOT EXISTS outbox"
    assert migration =~ "ALTER TABLE session_checkpoints"
    assert migration =~ "ALTER TABLE outbox"
    assert migration =~ "tenant_id TEXT NOT NULL"
    assert migration =~ "workspace_id TEXT NOT NULL"
    assert migration =~ "isolation_tier TEXT NOT NULL"
  end

  defp count_rows(table) do
    SQL.query!(Repo, "SELECT COUNT(*) FROM #{table}", []).rows
    |> List.first()
    |> List.first()
  end

  defp fixture do
    {fixture, _binding} = Code.eval_file(@fixture_path)
    fixture
  end
end
