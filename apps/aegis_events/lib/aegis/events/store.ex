defmodule Aegis.Events.Store do
  @moduledoc false

  alias Aegis.Events.{Catalog, Checkpoint, Envelope, Replay}
  alias Aegis.Repo
  alias Ecto.Adapters.SQL

  @checkpoint_triggers MapSet.new([
                         "session.created",
                         "session.hydrated",
                         "session.waiting",
                         "session.completed",
                         "session.failed",
                         "session.quarantined"
                       ])
  @terminal_session_events ["session.completed", "session.failed"]

  def reset! do
    SQL.query!(
      Repo,
      "TRUNCATE action_executions, worker_registrations, session_leases, outbox, session_checkpoints, session_events, sessions RESTART IDENTITY CASCADE",
      []
    )

    :ok
  end

  def sessions(scope \\ %{}) do
    scope = normalize_scope(scope)

    SQL.query!(
      Repo,
      """
      SELECT session_id, tenant_id, workspace_id, session_kind, requested_by, owner_node,
             isolation_tier, last_seq_no, last_event_hash, current_checkpoint_id, inserted_at, updated_at
      FROM sessions
      WHERE ($1::text IS NULL OR tenant_id = $1)
        AND ($2::text IS NULL OR workspace_id = $2)
      ORDER BY updated_at DESC, session_id ASC
      """,
      [scope.tenant_id, scope.workspace_id]
    )
    |> rows_to_maps()
    |> Enum.map(&normalize_map/1)
  end

  def session_exists?(session_id, scope \\ %{}) do
    not is_nil(fetch_session_row(session_id, normalize_scope(scope)))
  end

  def live_session_count(scope \\ %{}) do
    scope = normalize_scope(scope)

    SQL.query!(
      Repo,
      """
      SELECT COUNT(*)::bigint AS live_count
      FROM sessions AS s
      JOIN LATERAL (
        SELECT type
        FROM session_events AS e
        WHERE e.session_id = s.session_id
        ORDER BY e.seq_no DESC
        LIMIT 1
      ) AS latest_event ON TRUE
      WHERE ($1::text IS NULL OR s.tenant_id = $1)
        AND ($2::text IS NULL OR s.workspace_id = $2)
        AND latest_event.type <> ALL($3)
      """,
      [scope.tenant_id, scope.workspace_id, @terminal_session_events]
    )
    |> rows_to_maps()
    |> List.first()
    |> Map.fetch!(:live_count)
  end

  def events(session_id, scope \\ %{}) do
    scope = normalize_scope(scope)

    SQL.query!(
      Repo,
      """
      SELECT event_id, tenant_id, workspace_id, session_id, seq_no, type, event_version,
             occurred_at, recorded_at, actor_kind, actor_id, command_id, correlation_id,
             causation_id, trace_id, span_id, lease_epoch, idempotency_key,
             determinism_class, prev_event_hash, event_hash, payload
      FROM session_events
      WHERE session_id = $1
        AND ($2::text IS NULL OR tenant_id = $2)
        AND ($3::text IS NULL OR workspace_id = $3)
      ORDER BY seq_no ASC
      """,
      [session_id, scope.tenant_id, scope.workspace_id]
    )
    |> rows_to_maps()
    |> Enum.map(&to_envelope/1)
  end

  def checkpoints(session_id, scope \\ %{}) do
    scope = normalize_scope(scope)

    SQL.query!(
      Repo,
      """
      SELECT checkpoint_id, tenant_id, workspace_id, session_id, seq_no, payload, inserted_at
      FROM session_checkpoints
      WHERE session_id = $1
        AND ($2::text IS NULL OR tenant_id = $2)
        AND ($3::text IS NULL OR workspace_id = $3)
      ORDER BY seq_no ASC
      """,
      [session_id, scope.tenant_id, scope.workspace_id]
    )
    |> rows_to_maps()
    |> Enum.map(&to_checkpoint/1)
  end

  def latest_checkpoint(session_id, scope \\ %{}) do
    scope = normalize_scope(scope)

    SQL.query!(
      Repo,
      """
      SELECT checkpoint_id, tenant_id, workspace_id, session_id, seq_no, payload, inserted_at
      FROM session_checkpoints
      WHERE session_id = $1
        AND ($2::text IS NULL OR tenant_id = $2)
        AND ($3::text IS NULL OR workspace_id = $3)
      ORDER BY seq_no DESC
      LIMIT 1
      """,
      [session_id, scope.tenant_id, scope.workspace_id]
    )
    |> rows_to_maps()
    |> List.first()
    |> case do
      nil -> nil
      row -> to_checkpoint(row)
    end
  end

  def outbox(session_id, scope \\ %{}) do
    scope = normalize_scope(scope)

    SQL.query!(
      Repo,
      """
      SELECT outbox_id, tenant_id, workspace_id, session_id, event_id, event_type, status,
             subject, headers, payload, inserted_at, published_at
      FROM outbox
      WHERE session_id = $1
        AND ($2::text IS NULL OR tenant_id = $2)
        AND ($3::text IS NULL OR workspace_id = $3)
      ORDER BY inserted_at ASC, event_id ASC
      """,
      [session_id, scope.tenant_id, scope.workspace_id]
    )
    |> rows_to_maps()
    |> Enum.map(&normalize_map/1)
  end

  def historical_replay(session_id, scope \\ %{}) do
    scope = normalize_scope(scope)

    case fetch_session_row(session_id, scope) do
      nil ->
        {:error, :unknown_session}

      session_row ->
        checkpoint = latest_checkpoint(session_id, scope)
        timeline = events(session_id, scope)
        tail = tail_after_checkpoint(timeline, checkpoint)

        with :ok <- validate_replay_inputs(session_row, checkpoint, timeline),
             {:ok, replay_state} <- safe_replay(session_row, checkpoint, tail) do
          {:ok,
           %{
             timeline: timeline,
             replay_state: replay_state,
             latest_checkpoint: checkpoint,
             integrity_failure: nil
           }}
        else
          {:error, reason} ->
            {:ok, quarantine_replay_result(session_row, checkpoint, timeline, reason)}
        end
    end
  end

  def replay_at(session_id, seq_no), do: replay_at(session_id, seq_no, %{})

  def replay_at(session_id, seq_no, scope) when is_integer(seq_no) and seq_no >= 0 do
    scope = normalize_scope(scope)

    case fetch_session_row(session_id, scope) do
      nil ->
        {:error, :unknown_session}

      session_row ->
        timeline =
          session_id
          |> events(scope)
          |> Enum.filter(&(&1.seq_no <= seq_no))

        checkpoint =
          session_id
          |> checkpoints(scope)
          |> Enum.filter(&(&1.seq_no <= seq_no))
          |> List.last()

        tail = tail_after_checkpoint(timeline, checkpoint)

        with :ok <- validate_replay_inputs(session_row, checkpoint, timeline, expected_last_seq_no: seq_no),
             {:ok, replay_state} <- safe_replay(session_row, checkpoint, tail) do
          {:ok,
           %{
             timeline: timeline,
             replay_state: replay_state,
             latest_checkpoint: checkpoint,
             integrity_failure: nil
           }}
        else
          {:error, reason} ->
            {:ok, quarantine_replay_result(session_row, checkpoint, timeline, reason)}
        end
    end
  end

  def hydrate(session_id), do: hydrate(session_id, %{})

  def hydrate(session_id, scope) do
    scope = normalize_scope(scope)

    case fetch_session_row(session_id, scope) do
      nil ->
        {:error, :unknown_session}

      session_row ->
        checkpoint = latest_checkpoint(session_id, scope)
        timeline = events(session_id, scope)
        tail = tail_after_checkpoint(timeline, checkpoint)

        with :ok <- validate_replay_inputs(session_row, checkpoint, timeline),
             {:ok, replay_state} <- safe_replay(session_row, checkpoint, tail) do
          restored_event =
            build_checkpoint_restored(session_row, checkpoint, replay_state.last_seq_no)

          {:ok,
           %{
             checkpoint: checkpoint,
             tail_events: tail,
             replay_state: replay_state,
             restored_event: restored_event,
             integrity_failure: nil
           }}
        else
          {:error, reason} ->
            replay = quarantine_replay_result(session_row, checkpoint, timeline, reason)

            {:ok,
             %{
               checkpoint: checkpoint,
               tail_events: tail,
               replay_state: replay.replay_state,
               restored_event: nil,
               integrity_failure: replay.integrity_failure
             }}
        end
    end
  end

  def append(session_state, events, opts \\ []) do
    session_state = normalize_session_state(session_state)
    raw_events = Enum.map(List.wrap(events), &normalize_raw_event/1)

    with :ok <- ensure_events_known(raw_events) do
      Repo.transaction(fn ->
        ensure_session_row!(session_state)
        session_row = lock_session_row!(session_state.session_id)

        with :ok <- ensure_session_scope(session_row, session_state),
             :ok <- validate_seq(session_row, raw_events) do
          append_transaction(session_row, session_state, raw_events, opts)
        else
          {:error, reason} ->
            Repo.rollback(reason)
        end
      end)
      |> case do
        {:ok, result} -> {:ok, result}
        {:error, reason} -> {:error, reason}
      end
    end
  end

  defp append_transaction(session_row, session_state, raw_events, opts) do
    prev_hash = session_row.last_event_hash || "genesis"

    {persisted_events, final_hash} =
      Enum.map_reduce(raw_events, prev_hash, fn raw_event, acc_hash ->
        envelope = build_envelope(session_row, session_state, raw_event, acc_hash, opts)
        insert_event!(envelope)
        {envelope, envelope.event_hash}
      end)

    checkpoint? = should_checkpoint?(persisted_events, opts)
    last_event_seq_no = List.last(persisted_events).seq_no
    checkpoint_seq_no = if checkpoint?, do: last_event_seq_no + 1

    checkpoint_state =
      session_state
      |> Map.put(:last_seq_no, last_event_seq_no)

    checkpoint =
      if checkpoint? do
        checkpoint = build_checkpoint(checkpoint_state, checkpoint_seq_no)
        insert_checkpoint!(checkpoint)
        checkpoint
      end

    checkpoint_event =
      if checkpoint do
        checkpoint_created =
          build_checkpoint_created(session_row, session_state, checkpoint, final_hash, opts)

        insert_event!(checkpoint_created)
        checkpoint_created
      end

    timeline =
      if checkpoint_event do
        persisted_events ++ [checkpoint_event]
      else
        persisted_events
      end

    outbox_rows =
      timeline
      |> Enum.map(&build_outbox_row(session_row, &1))
      |> Enum.map(fn outbox_row ->
        insert_outbox_row!(outbox_row)
        outbox_row
      end)

    final_seq_no =
      case List.last(timeline) do
        nil -> session_row.last_seq_no
        envelope -> envelope.seq_no
      end

    updated_session_row =
      update_session_row!(
        session_row.session_id,
        session_state.owner_node,
        final_seq_no,
        List.last(timeline).event_hash,
        checkpoint && checkpoint.checkpoint_id
      )

    %{
      session: updated_session_row,
      persisted_events: timeline,
      checkpoint: checkpoint,
      outbox_entries: outbox_rows,
      last_seq_no: final_seq_no
    }
  end

  defp ensure_session_row!(session_state) do
    timestamp = now()

    SQL.query!(
      Repo,
      """
      INSERT INTO sessions (
        session_id, tenant_id, workspace_id, isolation_tier, session_kind, requested_by, owner_node,
        last_seq_no, last_event_hash, current_checkpoint_id, inserted_at, updated_at
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, 0, 'genesis', NULL, $8, $8)
      ON CONFLICT (session_id) DO NOTHING
      """,
      [
        session_state.session_id,
        session_state.tenant_id,
        session_state.workspace_id,
        Map.get(session_state, :isolation_tier, "tier_a"),
        Map.get(session_state, :session_kind, "browser_operation"),
        Map.get(session_state, :requested_by, "system"),
        Map.get(session_state, :owner_node, Atom.to_string(node())),
        timestamp
      ]
    )

    :ok
  end

  defp lock_session_row!(session_id) do
    case SQL.query!(
           Repo,
           """
           SELECT session_id, tenant_id, workspace_id, isolation_tier, session_kind, requested_by,
                  owner_node, last_seq_no, last_event_hash, current_checkpoint_id, inserted_at,
                  updated_at
           FROM sessions
           WHERE session_id = $1
           FOR UPDATE
           """,
           [session_id]
         )
         |> rows_to_maps()
         |> List.first() do
      nil -> Repo.rollback(:unknown_session)
      row -> normalize_map(row)
    end
  end

  defp fetch_session_row(session_id, scope) do
    scope = normalize_scope(scope)

    SQL.query!(
      Repo,
      """
      SELECT session_id, tenant_id, workspace_id, isolation_tier, session_kind, requested_by,
             owner_node, last_seq_no, last_event_hash, current_checkpoint_id, inserted_at,
             updated_at
      FROM sessions
      WHERE session_id = $1
        AND ($2::text IS NULL OR tenant_id = $2)
        AND ($3::text IS NULL OR workspace_id = $3)
      """,
      [session_id, scope.tenant_id, scope.workspace_id]
    )
    |> rows_to_maps()
    |> List.first()
    |> case do
      nil -> nil
      row -> normalize_map(row)
    end
  end

  defp update_session_row!(session_id, owner_node, last_seq_no, last_event_hash, checkpoint_id) do
    SQL.query!(
      Repo,
      """
      UPDATE sessions
      SET owner_node = $2,
          last_seq_no = $3,
          last_event_hash = $4,
          current_checkpoint_id = $5,
          updated_at = $6
      WHERE session_id = $1
      RETURNING session_id, tenant_id, workspace_id, isolation_tier, session_kind, requested_by,
                owner_node, last_seq_no, last_event_hash, current_checkpoint_id, inserted_at,
                updated_at
      """,
      [session_id, owner_node, last_seq_no, last_event_hash, checkpoint_id, now()]
    )
    |> rows_to_maps()
    |> List.first()
    |> normalize_map()
  end

  defp insert_event!(envelope) do
    SQL.query!(
      Repo,
      """
      INSERT INTO session_events (
        event_id, tenant_id, workspace_id, session_id, seq_no, type, event_version, occurred_at,
        recorded_at, actor_kind, actor_id, command_id, correlation_id, causation_id, trace_id,
        span_id, lease_epoch, idempotency_key, determinism_class, prev_event_hash, event_hash,
        payload
      )
      VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8,
        $9, $10, $11, $12, $13, $14, $15,
        $16, $17, $18, $19, $20, $21, $22
      )
      """,
      [
        envelope.event_id,
        envelope.tenant_id,
        envelope.workspace_id,
        envelope.session_id,
        envelope.seq_no,
        envelope.type,
        envelope.event_version,
        envelope.occurred_at,
        envelope.recorded_at,
        envelope.actor_kind,
        envelope.actor_id,
        envelope.command_id,
        envelope.correlation_id,
        envelope.causation_id,
        envelope.trace_id,
        envelope.span_id,
        envelope.lease_epoch,
        envelope.idempotency_key,
        envelope.determinism_class,
        envelope.prev_event_hash,
        envelope.event_hash,
        envelope.payload
      ]
    )
  end

  defp insert_checkpoint!(checkpoint) do
    SQL.query!(
      Repo,
      """
      INSERT INTO session_checkpoints (
        checkpoint_id, tenant_id, workspace_id, session_id, seq_no, payload, inserted_at
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      """,
      [
        checkpoint.checkpoint_id,
        checkpoint.tenant_id,
        checkpoint.workspace_id,
        checkpoint.session_id,
        checkpoint.seq_no,
        checkpoint.payload,
        checkpoint.inserted_at
      ]
    )
  end

  defp insert_outbox_row!(outbox_row) do
    SQL.query!(
      Repo,
      """
      INSERT INTO outbox (
        outbox_id, tenant_id, workspace_id, session_id, event_id, event_type, status, subject,
        headers, payload, inserted_at, published_at
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
      """,
      [
        outbox_row.outbox_id,
        outbox_row.tenant_id,
        outbox_row.workspace_id,
        outbox_row.session_id,
        outbox_row.event_id,
        outbox_row.event_type,
        outbox_row.status,
        outbox_row.subject,
        Map.get(outbox_row, :headers, %{}),
        outbox_row.payload,
        outbox_row.inserted_at,
        Map.get(outbox_row, :published_at)
      ]
    )
  end

  defp build_envelope(session_row, session_state, raw_event, prev_hash, opts) do
    metadata = Catalog.fetch!(raw_event.type)
    actor_id = Keyword.get(opts, :actor_id, Map.get(session_state, :owner_node, "system"))
    actor_kind = Keyword.get(opts, :actor_kind, "system")

    event_hash =
      hash_of(%{
        session_id: session_row.session_id,
        seq_no: raw_event.seq_no,
        type: raw_event.type,
        payload: raw_event.payload,
        prev_event_hash: prev_hash
      })

    %Envelope{
      event_id: "evt-#{session_row.session_id}-#{raw_event.seq_no}",
      tenant_id: session_row.tenant_id,
      workspace_id: session_row.workspace_id,
      session_id: session_row.session_id,
      seq_no: raw_event.seq_no,
      type: raw_event.type,
      event_version: metadata.version,
      occurred_at: raw_event.recorded_at,
      recorded_at: raw_event.recorded_at,
      actor_kind: actor_kind,
      actor_id: actor_id,
      command_id: Map.get(raw_event, :command_id),
      correlation_id: Map.get(raw_event, :correlation_id),
      causation_id: Map.get(raw_event, :causation_id),
      trace_id: Map.get(raw_event, :trace_id),
      span_id: Map.get(raw_event, :span_id),
      lease_epoch: Map.get(session_state, :lease_epoch, 0),
      idempotency_key: Map.get(raw_event, :idempotency_key),
      determinism_class: metadata.determinism_class,
      prev_event_hash: prev_hash,
      event_hash: event_hash,
      payload: raw_event.payload
    }
  end

  defp build_checkpoint(session_state, seq_no) do
    checkpoint_id = "ckp-#{session_state.session_id}-#{seq_no}"

    payload =
      session_state
      |> Map.put(:version, 1)
      |> Map.put(:latest_checkpoint_id, checkpoint_id)
      |> Map.take([
        :version,
        :tenant_id,
        :workspace_id,
        :session_id,
        :session_kind,
        :requested_by,
        :owner_node,
        :phase,
        :control_mode,
        :health,
        :wait_reason,
        :lease_epoch,
        :last_seq_no,
        :latest_checkpoint_id,
        :action_ledger,
        :pending_approvals,
        :deadlines,
        :child_agents,
        :browser_handles,
        :summary_capsule,
        :artifact_ids,
        :recent_artifacts,
        :latest_recovery_reason,
        :fenced
      ])

    %Checkpoint{
      checkpoint_id: checkpoint_id,
      tenant_id: session_state.tenant_id,
      workspace_id: session_state.workspace_id,
      session_id: session_state.session_id,
      seq_no: seq_no,
      payload: payload,
      inserted_at: now()
    }
  end

  defp build_checkpoint_created(session_row, session_state, checkpoint, prev_hash, opts) do
    raw_event = %{
      seq_no: checkpoint.seq_no,
      type: "checkpoint.created",
      payload: %{
        checkpoint_id: checkpoint.checkpoint_id,
        seq_no: checkpoint.payload.last_seq_no
      },
      recorded_at: checkpoint.inserted_at
    }

    build_envelope(session_row, session_state, raw_event, prev_hash, opts)
  end

  defp build_checkpoint_restored(_session_row, nil, _restored_seq_no), do: nil

  defp build_checkpoint_restored(session_row, checkpoint, restored_seq_no) do
    raw_event = %{
      seq_no: restored_seq_no,
      type: "checkpoint.restored",
      payload: %{
        checkpoint_id: checkpoint.checkpoint_id,
        restored_seq_no: restored_seq_no
      },
      recorded_at: now()
    }

    build_envelope(
      session_row,
      %{
        lease_epoch: Map.get(checkpoint.payload, :lease_epoch, 0),
        owner_node: Map.get(checkpoint.payload, :owner_node, "system")
      },
      raw_event,
      "historical",
      []
    )
  end

  defp build_outbox_row(session_row, envelope) do
    %{
      outbox_id: "outbox-#{envelope.event_id}",
      tenant_id: session_row.tenant_id,
      workspace_id: session_row.workspace_id,
      session_id: session_row.session_id,
      event_id: envelope.event_id,
      event_type: envelope.type,
      status: "pending",
      subject: "aegis.v1.event.#{String.replace(envelope.type, ".", "_")}",
      headers: build_outbox_headers(session_row, envelope),
      payload: envelope.payload,
      inserted_at: envelope.recorded_at,
      published_at: nil
    }
  end

  defp build_outbox_headers(session_row, envelope) do
    %{
      "x-aegis-trace-id" => envelope.trace_id,
      "x-aegis-tenant-id" => envelope.tenant_id,
      "x-aegis-workspace-id" => envelope.workspace_id,
      "x-aegis-session-id" => envelope.session_id,
      "x-aegis-lease-epoch" => to_string(envelope.lease_epoch),
      "x-aegis-contract-version" => "v1",
      "x-aegis-isolation-tier" =>
        Map.get(envelope.payload, :isolation_tier, Map.get(session_row, :isolation_tier, "tier_a"))
    }
  end

  defp should_checkpoint?(events, opts) do
    explicit = Keyword.get(opts, :checkpoint, :auto)

    case explicit do
      true -> true
      false -> false
      :auto -> Enum.any?(events, &MapSet.member?(@checkpoint_triggers, &1.type))
    end
  end

  defp ensure_events_known(events) do
    case Enum.find(events, &(not Catalog.known?(&1.type))) do
      nil -> :ok
      event -> {:error, {:unknown_event_type, event.type}}
    end
  end

  defp validate_replay_inputs(session_row, checkpoint, timeline, opts \\ []) do
    expected_last_seq_no =
      Keyword.get(
        opts,
        :expected_last_seq_no,
        if(timeline == [], do: 0, else: session_row.last_seq_no)
      )

    with :ok <- ensure_events_known(timeline),
         :ok <- validate_checkpoint_integrity(session_row, checkpoint),
         :ok <- validate_replay_timeline(timeline, expected_last_seq_no) do
      :ok
    end
  end

  defp validate_checkpoint_integrity(_session_row, nil), do: :ok

  defp validate_checkpoint_integrity(session_row, checkpoint) do
    payload = checkpoint.payload

    cond do
      checkpoint.tenant_id != session_row.tenant_id ->
        {:error,
         {:checkpoint_corruption, :tenant_id_mismatch,
          %{checkpoint_id: checkpoint.checkpoint_id, tenant_id: checkpoint.tenant_id}}}

      checkpoint.workspace_id != session_row.workspace_id ->
        {:error,
         {:checkpoint_corruption, :workspace_id_mismatch,
          %{checkpoint_id: checkpoint.checkpoint_id, workspace_id: checkpoint.workspace_id}}}

      Map.get(payload, :session_id) not in [nil, session_row.session_id] ->
        {:error,
         {:checkpoint_corruption, :session_id_mismatch,
          %{checkpoint_id: checkpoint.checkpoint_id, session_id: Map.get(payload, :session_id)}}}

      Map.get(payload, :tenant_id) not in [nil, session_row.tenant_id] ->
        {:error,
         {:checkpoint_corruption, :tenant_id_mismatch,
          %{checkpoint_id: checkpoint.checkpoint_id, tenant_id: Map.get(payload, :tenant_id)}}}

      Map.get(payload, :workspace_id) not in [nil, session_row.workspace_id] ->
        {:error,
         {:checkpoint_corruption, :workspace_id_mismatch,
          %{checkpoint_id: checkpoint.checkpoint_id, workspace_id: Map.get(payload, :workspace_id)}}}

      Map.get(payload, :latest_checkpoint_id) not in [nil, checkpoint.checkpoint_id] ->
        {:error,
         {:checkpoint_corruption, :latest_checkpoint_id_mismatch,
          %{
            checkpoint_id: checkpoint.checkpoint_id,
            latest_checkpoint_id: Map.get(payload, :latest_checkpoint_id)
          }}}

      Map.get(payload, :last_seq_no) != nil and Map.get(payload, :last_seq_no) != checkpoint.seq_no - 1 ->
        {:error,
         {:checkpoint_corruption, :last_seq_no_mismatch,
          %{
            checkpoint_id: checkpoint.checkpoint_id,
            checkpoint_seq_no: checkpoint.seq_no,
            payload_last_seq_no: Map.get(payload, :last_seq_no)
          }}}

      Map.get(payload, :phase) not in [nil, "provisioning", "hydrating", "active", "waiting", "cancelling", "terminal"] ->
        {:error,
         {:checkpoint_corruption, :invalid_phase,
          %{checkpoint_id: checkpoint.checkpoint_id, phase: Map.get(payload, :phase)}}}

      Map.get(payload, :control_mode) not in [nil, "autonomous", "supervised", "human_control", "paused"] ->
        {:error,
         {:checkpoint_corruption, :invalid_control_mode,
          %{checkpoint_id: checkpoint.checkpoint_id, control_mode: Map.get(payload, :control_mode)}}}

      Map.get(payload, :health) not in [nil, "healthy", "degraded", "quarantined"] ->
        {:error,
         {:checkpoint_corruption, :invalid_health,
          %{checkpoint_id: checkpoint.checkpoint_id, health: Map.get(payload, :health)}}}

      Map.get(payload, :wait_reason) not in [nil, "none", "action", "approval", "timer", "external_dependency", "operator", "lease_recovery"] ->
        {:error,
         {:checkpoint_corruption, :invalid_wait_reason,
          %{checkpoint_id: checkpoint.checkpoint_id, wait_reason: Map.get(payload, :wait_reason)}}}

      true ->
        :ok
    end
  end

  defp validate_replay_timeline([], 0), do: :ok

  defp validate_replay_timeline(timeline, expected_last_seq_no) do
    seq_validation =
      timeline
      |> Enum.map(& &1.seq_no)
      |> validate_replay_seq(expected_last_seq_no)

    with :ok <- seq_validation do
      timeline
      |> Enum.reduce_while("genesis", fn event, expected_prev_hash ->
        expected_hash =
          hash_of(%{
            session_id: event.session_id,
            seq_no: event.seq_no,
            type: event.type,
            payload: event.payload,
            prev_event_hash: event.prev_event_hash
          })

        cond do
          event.prev_event_hash != expected_prev_hash ->
            {:halt,
             {:error,
              {:event_corruption, :hash_chain_mismatch,
               %{
                 seq_no: event.seq_no,
                 expected_prev_event_hash: expected_prev_hash,
                 actual_prev_event_hash: event.prev_event_hash
               }}}}

          event.event_hash != expected_hash ->
            {:halt,
             {:error,
              {:event_corruption, :event_hash_mismatch,
               %{
                 seq_no: event.seq_no,
                 expected_event_hash: expected_hash,
                 actual_event_hash: event.event_hash
               }}}}

          true ->
            {:cont, event.event_hash}
        end
      end)
      |> case do
        {:error, reason} -> {:error, reason}
        _hash -> :ok
      end
    end
  end

  defp validate_replay_seq([], expected_last_seq_no) when expected_last_seq_no in [nil, 0], do: :ok

  defp validate_replay_seq(actual, expected_last_seq_no) do
    expected = Enum.to_list(1..length(actual))

    cond do
      actual != expected ->
        {:error, {:event_corruption, :seq_gap, %{expected: expected, actual: actual}}}

      expected_last_seq_no != nil and List.last(actual) != expected_last_seq_no ->
        {:error,
         {:event_corruption, :session_row_seq_mismatch,
          %{expected_last_seq_no: expected_last_seq_no, actual_last_seq_no: List.last(actual)}}}

      true ->
        :ok
    end
  end

  defp safe_replay(session_row, checkpoint, events) do
    {:ok, Replay.replay(session_row, checkpoint, events)}
  rescue
    error ->
      {:error, {:replay_failure, Exception.message(error)}}
  end

  defp quarantine_replay_result(session_row, checkpoint, timeline, reason) do
    base_state =
      try do
        Replay.from_checkpoint(checkpoint, session_row)
      rescue
        _error -> Replay.initial_state(session_row)
      end

    replay_state =
      base_state
      |> Map.put(:phase, "waiting")
      |> Map.put(:health, "quarantined")
      |> Map.put(:wait_reason, "external_dependency")
      |> Map.put(:fenced, true)
      |> Map.put(:last_seq_no, infer_last_seq_no(timeline, session_row))
      |> Map.put(:latest_checkpoint_id, if(checkpoint, do: checkpoint.checkpoint_id, else: session_row.current_checkpoint_id))
      |> Map.put(:latest_recovery_reason, replay_failure_reason(reason))

    %{
      timeline: timeline,
      replay_state: replay_state,
      latest_checkpoint: checkpoint,
      integrity_failure: integrity_failure(reason)
    }
  end

  defp infer_last_seq_no([], session_row), do: session_row.last_seq_no
  defp infer_last_seq_no(timeline, _session_row), do: List.last(timeline).seq_no

  defp replay_failure_reason({:event_corruption, kind, _details}), do: "event_corruption:#{kind}"
  defp replay_failure_reason({:checkpoint_corruption, kind, _details}), do: "checkpoint_corruption:#{kind}"
  defp replay_failure_reason({:replay_failure, message}), do: "replay_failure:#{message}"
  defp replay_failure_reason(other), do: "replay_failure:#{inspect(other)}"

  defp integrity_failure({:event_corruption, kind, details}) do
    %{kind: "event_corruption", code: to_string(kind), details: details}
  end

  defp integrity_failure({:checkpoint_corruption, kind, details}) do
    %{kind: "checkpoint_corruption", code: to_string(kind), details: details}
  end

  defp integrity_failure({:replay_failure, message}) do
    %{kind: "replay_failure", code: "replay_failure", details: %{message: message}}
  end

  defp integrity_failure(reason) do
    %{kind: "replay_failure", code: "unexpected", details: %{reason: inspect(reason)}}
  end

  defp validate_seq(session_row, raw_events) do
    starting_seq = session_row.last_seq_no + 1
    expected = Enum.to_list(starting_seq..(starting_seq + length(raw_events) - 1))
    actual = Enum.map(raw_events, & &1.seq_no)

    if actual == expected do
      :ok
    else
      {:error, {:invalid_seq, expected, actual}}
    end
  end

  defp ensure_session_scope(session_row, session_state) do
    cond do
      Map.get(session_state, :tenant_id, session_row.tenant_id) != session_row.tenant_id ->
        {:error,
         {:session_scope_mismatch, :tenant_id,
          %{expected: session_row.tenant_id, actual: Map.get(session_state, :tenant_id)}}}

      Map.get(session_state, :workspace_id, session_row.workspace_id) != session_row.workspace_id ->
        {:error,
         {:session_scope_mismatch, :workspace_id,
          %{expected: session_row.workspace_id, actual: Map.get(session_state, :workspace_id)}}}

      true ->
        :ok
    end
  end

  defp tail_after_checkpoint(timeline, nil), do: timeline

  defp tail_after_checkpoint(timeline, checkpoint) do
    Enum.filter(timeline, &(&1.seq_no > checkpoint.seq_no))
  end

  defp to_envelope(row) do
    %Envelope{
      event_id: row.event_id,
      tenant_id: row.tenant_id,
      workspace_id: row.workspace_id,
      session_id: row.session_id,
      seq_no: row.seq_no,
      type: row.type,
      event_version: row.event_version,
      occurred_at: row.occurred_at,
      recorded_at: row.recorded_at,
      actor_kind: row.actor_kind,
      actor_id: row.actor_id,
      command_id: row.command_id,
      correlation_id: row.correlation_id,
      causation_id: row.causation_id,
      trace_id: row.trace_id,
      span_id: row.span_id,
      lease_epoch: row.lease_epoch,
      idempotency_key: row.idempotency_key,
      determinism_class: row.determinism_class,
      prev_event_hash: row.prev_event_hash,
      event_hash: row.event_hash,
      payload: normalize_map(row.payload)
    }
  end

  defp to_checkpoint(row) do
    %Checkpoint{
      checkpoint_id: row.checkpoint_id,
      tenant_id: row.tenant_id,
      workspace_id: row.workspace_id,
      session_id: row.session_id,
      seq_no: row.seq_no,
      payload: normalize_map(row.payload),
      inserted_at: row.inserted_at
    }
  end

  defp rows_to_maps(%{columns: columns, rows: rows}) do
    Enum.map(rows, fn row ->
      columns
      |> Enum.zip(row)
      |> Enum.into(%{})
      |> normalize_map()
    end)
  end

  defp normalize_raw_event(event) do
    event =
      case event do
        %{__struct__: _} -> Map.from_struct(event)
        map when is_map(map) -> map
      end

    %{
      seq_no: event.seq_no,
      type: event.type,
      payload: normalize_map(event.payload),
      recorded_at: Map.get(event, :recorded_at, now()),
      command_id: Map.get(event, :command_id),
      correlation_id: Map.get(event, :correlation_id),
      causation_id: Map.get(event, :causation_id),
      trace_id: Map.get(event, :trace_id),
      span_id: Map.get(event, :span_id),
      idempotency_key: Map.get(event, :idempotency_key)
    }
  end

  defp normalize_session_state(state) do
    state =
      case state do
        %{__struct__: _} -> Map.from_struct(state)
        map when is_map(map) -> map
      end

    state
    |> normalize_map()
    |> Map.update(:phase, "provisioning", &normalize_enum/1)
    |> Map.update(:control_mode, "autonomous", &normalize_enum/1)
    |> Map.update(:health, "healthy", &normalize_enum/1)
    |> Map.update(:wait_reason, "none", &normalize_enum/1)
    |> Map.put_new(:phase, "provisioning")
    |> Map.put_new(:control_mode, "autonomous")
    |> Map.put_new(:health, "healthy")
    |> Map.put_new(:wait_reason, "none")
    |> Map.put_new(:lease_epoch, 0)
    |> Map.put_new(:last_seq_no, 0)
    |> Map.put_new(:deadlines, [])
    |> Map.put_new(:pending_approvals, [])
    |> Map.put_new(:action_ledger, [])
    |> Map.put_new(:child_agents, [])
    |> Map.put_new(:browser_handles, [])
    |> Map.put_new(:summary_capsule, %{
      planner_summary: "",
      salient_facts: [],
      operator_notes: []
    })
    |> Map.put_new(:artifact_ids, [])
    |> Map.put_new(:recent_artifacts, [])
    |> Map.put_new(:latest_recovery_reason, nil)
    |> Map.put_new(:fenced, false)
    |> Map.put_new(:owner_node, Atom.to_string(node()))
  end

  defp normalize_map(%_{} = value), do: value

  defp normalize_map(value) when is_map(value) do
    value
    |> Enum.map(fn {key, item} -> {normalize_key(key), normalize_map(item)} end)
    |> Enum.into(%{})
  end

  defp normalize_map(value) when is_list(value), do: Enum.map(value, &normalize_map/1)
  defp normalize_map(value), do: value

  defp normalize_enum(value) when is_atom(value), do: Atom.to_string(value)
  defp normalize_enum(value), do: value

  defp normalize_key(key) when is_atom(key), do: key

  defp normalize_key(key) when is_binary(key) do
    try do
      String.to_existing_atom(key)
    rescue
      ArgumentError -> key
    end
  end

  defp normalize_scope(nil), do: %{tenant_id: nil, workspace_id: nil}

  defp normalize_scope(scope) when is_list(scope) or is_map(scope) do
    scope =
      scope
      |> Map.new()
      |> normalize_map()

    %{
      tenant_id: Map.get(scope, :tenant_id),
      workspace_id: Map.get(scope, :workspace_id)
    }
  end

  defp hash_of(term) do
    term
    |> canonicalize()
    |> :erlang.term_to_binary()
    |> then(&:crypto.hash(:sha256, &1))
    |> Base.encode16(case: :lower)
  end

  defp canonicalize(value) when is_map(value) do
    value
    |> Enum.map(fn {key, item} -> {key, canonicalize(item)} end)
    |> Enum.sort_by(fn {key, _item} -> to_string(key) end)
  end

  defp canonicalize(value) when is_list(value), do: Enum.map(value, &canonicalize/1)
  defp canonicalize(value), do: value

  defp now, do: DateTime.utc_now() |> DateTime.truncate(:second)
end
