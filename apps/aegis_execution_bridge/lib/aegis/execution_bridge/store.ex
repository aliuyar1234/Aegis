defmodule Aegis.ExecutionBridge.Store do
  @moduledoc false

  alias Aegis.ExecutionBridge.Guardrails
  alias Aegis.Repo
  alias Ecto.Adapters.SQL

  @terminal_statuses ["succeeded", "failed", "cancelled", "lost", "uncertain"]

  def claim_outbox_rows(event_types, limit \\ 50) do
    Repo.transaction(fn ->
      rows =
        SQL.query!(
          Repo,
          """
          SELECT outbox_id, tenant_id, workspace_id, session_id, event_id, event_type, status,
                 subject, headers, payload, inserted_at, published_at
          FROM outbox
          WHERE status = 'pending'
            AND event_type = ANY($1)
          ORDER BY inserted_at ASC, event_id ASC
          LIMIT $2
          FOR UPDATE SKIP LOCKED
          """,
          [event_types, limit]
        )
        |> rows_to_maps()

      Enum.each(rows, fn row ->
        SQL.query!(Repo, "UPDATE outbox SET status = 'publishing' WHERE outbox_id = $1", [
          row.outbox_id
        ])
      end)

      Enum.map(rows, &normalize_map/1)
    end)
    |> unwrap_transaction()
  end

  def mark_outbox_published(outbox_id) do
    SQL.query!(
      Repo,
      """
      UPDATE outbox
      SET status = 'published',
          published_at = $2
      WHERE outbox_id = $1
      """,
      [outbox_id, now()]
    )

    :ok
  end

  def release_outbox(outbox_id) do
    SQL.query!(
      Repo,
      """
      UPDATE outbox
      SET status = 'pending',
          published_at = NULL
      WHERE outbox_id = $1
      """,
      [outbox_id]
    )

    :ok
  end

  def upsert_worker_registration(attrs) do
    Guardrails.assert_write_allowed!("worker_registrations")

    attrs = normalize_map(Map.new(attrs))
    current_time = now()
    last_seen_at = parse_datetime(Map.get(attrs, :last_seen_at, current_time))

    SQL.query!(
      Repo,
      """
      INSERT INTO worker_registrations (
        worker_id, worker_kind, worker_version, supported_contract_versions,
        advertised_capacity, available_capacity, attributes, status, last_seen_at,
        inserted_at, updated_at
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $10)
      ON CONFLICT (worker_id) DO UPDATE
      SET worker_kind = EXCLUDED.worker_kind,
          worker_version = EXCLUDED.worker_version,
          supported_contract_versions = EXCLUDED.supported_contract_versions,
          advertised_capacity = EXCLUDED.advertised_capacity,
          available_capacity = EXCLUDED.available_capacity,
          attributes = EXCLUDED.attributes,
          status = EXCLUDED.status,
          last_seen_at = EXCLUDED.last_seen_at,
          updated_at = EXCLUDED.updated_at
      RETURNING worker_id, worker_kind, worker_version, supported_contract_versions,
                advertised_capacity, available_capacity, attributes, status, last_seen_at,
                inserted_at, updated_at
      """,
      [
        Map.fetch!(attrs, :worker_id),
        Map.fetch!(attrs, :worker_kind),
        Map.get(attrs, :worker_version, "unknown"),
        Map.get(attrs, :supported_contract_versions, []),
        Map.get(attrs, :advertised_capacity, 0),
        Map.get(attrs, :available_capacity, Map.get(attrs, :advertised_capacity, 0)),
        Map.get(attrs, :attributes, %{}),
        Map.get(attrs, :status, "active"),
        last_seen_at,
        current_time
      ]
    )
    |> rows_to_maps()
    |> List.first()
    |> normalize_map()
  end

  def fetch_worker_registration(worker_id) do
    SQL.query!(
      Repo,
      """
      SELECT worker_id, worker_kind, worker_version, supported_contract_versions,
             advertised_capacity, available_capacity, attributes, status, last_seen_at,
             inserted_at, updated_at
      FROM worker_registrations
      WHERE worker_id = $1
      """,
      [worker_id]
    )
    |> rows_to_maps()
    |> List.first()
    |> case do
      nil -> nil
      row -> normalize_map(row)
    end
  end

  def worker_registrations do
    SQL.query!(
      Repo,
      """
      SELECT worker_id, worker_kind, worker_version, supported_contract_versions,
             advertised_capacity, available_capacity, attributes, status, last_seen_at,
             inserted_at, updated_at
      FROM worker_registrations
      ORDER BY last_seen_at DESC, worker_id ASC
      """,
      []
    )
    |> rows_to_maps()
    |> Enum.map(&normalize_map/1)
  end

  def upsert_execution(attrs) do
    Guardrails.assert_write_allowed!("action_executions")

    attrs = normalize_map(Map.new(attrs))
    current_time = now()

    SQL.query!(
      Repo,
      """
      INSERT INTO action_executions (
        execution_id, tenant_id, workspace_id, session_id, action_id, worker_kind, worker_id,
        contract_version, dispatch_subject, trace_id, idempotency_key, isolation_tier, status,
        lease_epoch, accept_deadline, soft_deadline, hard_deadline, accepted_at,
        last_progress_seq, last_heartbeat_seq, last_heartbeat_at, cancellation_reason,
        cancellation_requested_at, completed_at, failed_at, failure_error_code,
        failure_error_class, retryable, safe_to_retry, compensation_possible,
        uncertain_side_effect, result_artifact_id, normalized_result, last_payload,
        inserted_at, updated_at
      )
      VALUES (
        $1, $2, $3, $4, $5, $6, $7,
        $8, $9, $10, $11, $12, $13,
        $14, $15, $16, $17, $18,
        $19, $20, $21, $22,
        $23, $24, $25, $26,
        $27, $28, $29, $30,
        $31, $32, $33, $34,
        $35, $35
      )
      ON CONFLICT (session_id, action_id) DO UPDATE
      SET worker_kind = EXCLUDED.worker_kind,
          contract_version = EXCLUDED.contract_version,
          dispatch_subject = EXCLUDED.dispatch_subject,
          trace_id = EXCLUDED.trace_id,
          idempotency_key = EXCLUDED.idempotency_key,
          isolation_tier = EXCLUDED.isolation_tier,
          status = EXCLUDED.status,
          lease_epoch = EXCLUDED.lease_epoch,
          accept_deadline = EXCLUDED.accept_deadline,
          soft_deadline = EXCLUDED.soft_deadline,
          hard_deadline = EXCLUDED.hard_deadline,
          updated_at = EXCLUDED.updated_at
      RETURNING execution_id, tenant_id, workspace_id, session_id, action_id, worker_kind,
                worker_id, contract_version, dispatch_subject, trace_id, idempotency_key,
                isolation_tier, status, lease_epoch, accept_deadline, soft_deadline,
                hard_deadline, accepted_at, last_progress_seq, last_heartbeat_seq,
                last_heartbeat_at, cancellation_reason, cancellation_requested_at,
                completed_at, failed_at, failure_error_code, failure_error_class, retryable,
                safe_to_retry, compensation_possible, uncertain_side_effect, result_artifact_id,
                normalized_result, last_payload, inserted_at, updated_at
      """,
      [
        Map.fetch!(attrs, :execution_id),
        Map.fetch!(attrs, :tenant_id),
        Map.fetch!(attrs, :workspace_id),
        Map.fetch!(attrs, :session_id),
        Map.fetch!(attrs, :action_id),
        Map.fetch!(attrs, :worker_kind),
        Map.get(attrs, :worker_id),
        Map.fetch!(attrs, :contract_version),
        Map.fetch!(attrs, :dispatch_subject),
        Map.get(attrs, :trace_id),
        Map.get(attrs, :idempotency_key),
        Map.get(attrs, :isolation_tier, "tier_a"),
        Map.get(attrs, :status, "dispatched"),
        Map.fetch!(attrs, :lease_epoch),
        parse_datetime(Map.get(attrs, :accept_deadline)),
        parse_datetime(Map.get(attrs, :soft_deadline)),
        parse_datetime(Map.get(attrs, :hard_deadline)),
        parse_datetime(Map.get(attrs, :accepted_at)),
        Map.get(attrs, :last_progress_seq, 0),
        Map.get(attrs, :last_heartbeat_seq, 0),
        parse_datetime(Map.get(attrs, :last_heartbeat_at)),
        Map.get(attrs, :cancellation_reason),
        parse_datetime(Map.get(attrs, :cancellation_requested_at)),
        parse_datetime(Map.get(attrs, :completed_at)),
        parse_datetime(Map.get(attrs, :failed_at)),
        Map.get(attrs, :failure_error_code),
        Map.get(attrs, :failure_error_class),
        Map.get(attrs, :retryable),
        Map.get(attrs, :safe_to_retry),
        Map.get(attrs, :compensation_possible),
        Map.get(attrs, :uncertain_side_effect, false),
        Map.get(attrs, :result_artifact_id),
        Map.get(attrs, :normalized_result),
        Map.get(attrs, :last_payload, %{}),
        current_time
      ]
    )
    |> rows_to_maps()
    |> List.first()
    |> normalize_map()
  end

  def fetch_execution(execution_id, scope \\ %{}) do
    scope = normalize_scope(scope)

    SQL.query!(
      Repo,
      """
      SELECT execution_id, tenant_id, workspace_id, session_id, action_id, worker_kind,
             worker_id, contract_version, dispatch_subject, trace_id, idempotency_key,
             isolation_tier, status, lease_epoch, accept_deadline, soft_deadline,
             hard_deadline, accepted_at, last_progress_seq, last_heartbeat_seq,
             last_heartbeat_at, cancellation_reason, cancellation_requested_at, completed_at,
             failed_at, failure_error_code, failure_error_class, retryable, safe_to_retry,
             compensation_possible, uncertain_side_effect, result_artifact_id, normalized_result,
             last_payload, inserted_at, updated_at
      FROM action_executions
      WHERE execution_id = $1
        AND ($2::text IS NULL OR tenant_id = $2)
        AND ($3::text IS NULL OR workspace_id = $3)
      """,
      [execution_id, scope.tenant_id, scope.workspace_id]
    )
    |> rows_to_maps()
    |> List.first()
    |> case do
      nil -> nil
      row -> normalize_map(row)
    end
  end

  def fetch_execution_by_action(session_id, action_id, scope \\ %{}) do
    scope = normalize_scope(scope)

    SQL.query!(
      Repo,
      """
      SELECT execution_id, tenant_id, workspace_id, session_id, action_id, worker_kind,
             worker_id, contract_version, dispatch_subject, trace_id, idempotency_key,
             isolation_tier, status, lease_epoch, accept_deadline, soft_deadline,
             hard_deadline, accepted_at, last_progress_seq, last_heartbeat_seq,
             last_heartbeat_at, cancellation_reason, cancellation_requested_at, completed_at,
             failed_at, failure_error_code, failure_error_class, retryable, safe_to_retry,
             compensation_possible, uncertain_side_effect, result_artifact_id, normalized_result,
             last_payload, inserted_at, updated_at
      FROM action_executions
      WHERE session_id = $1
        AND action_id = $2
        AND ($3::text IS NULL OR tenant_id = $3)
        AND ($4::text IS NULL OR workspace_id = $4)
      """,
      [session_id, action_id, scope.tenant_id, scope.workspace_id]
    )
    |> rows_to_maps()
    |> List.first()
    |> case do
      nil -> nil
      row -> normalize_map(row)
    end
  end

  def mark_execution_accepted(execution_id, attrs) do
    update_execution!(execution_id, %{
      worker_id: Map.fetch!(attrs, :worker_id),
      status: "accepted",
      accepted_at: Map.fetch!(attrs, :accepted_at),
      last_heartbeat_at: Map.fetch!(attrs, :accepted_at),
      last_payload: attrs
    })
  end

  def mark_execution_progress(execution_id, attrs) do
    existing = fetch_execution(execution_id)

    if existing == nil or
         Map.get(attrs, :progress_seq, 0) <= Map.get(existing, :last_progress_seq, 0) do
      {:duplicate, existing}
    else
      {:updated,
       update_execution!(execution_id, %{
         status: "in_progress",
         last_progress_seq: Map.fetch!(attrs, :progress_seq),
         last_payload: attrs,
         last_heartbeat_at: Map.fetch!(attrs, :observed_at)
       })}
    end
  end

  def mark_execution_heartbeat(execution_id, attrs) do
    existing = fetch_execution(execution_id)

    if existing == nil or
         Map.get(attrs, :heartbeat_seq, 0) <= Map.get(existing, :last_heartbeat_seq, 0) do
      existing
    else
      update_execution!(execution_id, %{
        last_heartbeat_seq: Map.fetch!(attrs, :heartbeat_seq),
        last_heartbeat_at: Map.fetch!(attrs, :observed_at),
        last_payload: attrs
      })
    end
  end

  def mark_execution_completed(execution_id, attrs) do
    update_execution!(execution_id, %{
      status: "succeeded",
      completed_at: Map.fetch!(attrs, :completed_at),
      result_artifact_id: Map.get(attrs, :raw_result_artifact_id),
      normalized_result: Map.get(attrs, :normalized_result),
      last_payload: attrs
    })
  end

  def mark_execution_failed(execution_id, attrs) do
    status = if Map.get(attrs, :uncertain_side_effect, false), do: "uncertain", else: "failed"

    update_execution!(execution_id, %{
      status: status,
      failed_at: Map.fetch!(attrs, :failed_at),
      failure_error_code: Map.fetch!(attrs, :error_code),
      failure_error_class: Map.fetch!(attrs, :error_class),
      retryable: Map.get(attrs, :retryable),
      safe_to_retry: Map.get(attrs, :safe_to_retry),
      compensation_possible: Map.get(attrs, :compensation_possible),
      uncertain_side_effect: Map.get(attrs, :uncertain_side_effect, false),
      result_artifact_id: Map.get(attrs, :details_artifact_id),
      last_payload: attrs
    })
  end

  def mark_execution_cancel_requested(execution_id, attrs) do
    update_execution!(execution_id, %{
      status: "cancellation_requested",
      cancellation_reason: Map.fetch!(attrs, :reason),
      cancellation_requested_at: Map.fetch!(attrs, :cancel_requested_at),
      last_payload: attrs
    })
  end

  def mark_execution_cancelled(execution_id, attrs) do
    update_execution!(execution_id, %{
      status: "cancelled",
      worker_id: Map.fetch!(attrs, :worker_id),
      completed_at: Map.fetch!(attrs, :cancelled_at),
      cancellation_reason: Map.get(attrs, :reason),
      last_payload: attrs
    })
  end

  def mark_execution_lost(execution_id, attrs) do
    update_execution!(execution_id, %{
      status: "lost",
      uncertain_side_effect: Map.get(attrs, :uncertain_side_effect, true),
      last_payload: attrs
    })
  end

  def nonterminal_executions do
    SQL.query!(
      Repo,
      """
      SELECT execution_id, tenant_id, workspace_id, session_id, action_id, worker_kind,
             worker_id, contract_version, dispatch_subject, trace_id, idempotency_key,
             isolation_tier, status, lease_epoch, accept_deadline, soft_deadline,
             hard_deadline, accepted_at, last_progress_seq, last_heartbeat_seq,
             last_heartbeat_at, cancellation_reason, cancellation_requested_at, completed_at,
             failed_at, failure_error_code, failure_error_class, retryable, safe_to_retry,
             compensation_possible, uncertain_side_effect, result_artifact_id, normalized_result,
             last_payload, inserted_at, updated_at
      FROM action_executions
      WHERE status <> ALL($1)
      ORDER BY inserted_at ASC
      """,
      [@terminal_statuses]
    )
    |> rows_to_maps()
    |> Enum.map(&normalize_map/1)
  end

  def nonterminal_execution_count(scope \\ %{}, filters \\ []) do
    scope = normalize_scope(scope)
    filters = filters |> Enum.into(%{}) |> normalize_map()

    SQL.query!(
      Repo,
      """
      SELECT COUNT(*)::bigint AS execution_count
      FROM action_executions
      WHERE status <> ALL($1)
        AND ($2::text IS NULL OR tenant_id = $2)
        AND ($3::text IS NULL OR workspace_id = $3)
        AND ($4::text IS NULL OR worker_kind = $4)
        AND (
          $5::boolean IS NULL OR
          COALESCE((last_payload->>'mutating')::boolean, false) = $5
        )
      """,
      [
        @terminal_statuses,
        scope.tenant_id,
        scope.workspace_id,
        Map.get(filters, :worker_kind),
        Map.get(filters, :mutating)
      ]
    )
    |> rows_to_maps()
    |> List.first()
    |> Map.fetch!(:execution_count)
  end

  defp update_execution!(execution_id, attrs) do
    Guardrails.assert_write_allowed!("action_executions")

    current =
      fetch_execution(execution_id) ||
        raise ArgumentError, "unknown execution #{inspect(execution_id)}"

    merged =
      current
      |> Map.merge(normalize_map(attrs))
      |> Map.put(:updated_at, now())

    SQL.query!(
      Repo,
      """
      UPDATE action_executions
      SET worker_kind = $2,
          worker_id = $3,
          contract_version = $4,
          dispatch_subject = $5,
          trace_id = $6,
          idempotency_key = $7,
          isolation_tier = $8,
          status = $9,
          lease_epoch = $10,
          accept_deadline = $11,
          soft_deadline = $12,
          hard_deadline = $13,
          accepted_at = $14,
          last_progress_seq = $15,
          last_heartbeat_seq = $16,
          last_heartbeat_at = $17,
          cancellation_reason = $18,
          cancellation_requested_at = $19,
          completed_at = $20,
          failed_at = $21,
          failure_error_code = $22,
          failure_error_class = $23,
          retryable = $24,
          safe_to_retry = $25,
          compensation_possible = $26,
          uncertain_side_effect = $27,
          result_artifact_id = $28,
          normalized_result = $29,
          last_payload = $30,
          updated_at = $31
      WHERE execution_id = $1
      RETURNING execution_id, tenant_id, workspace_id, session_id, action_id, worker_kind,
                worker_id, contract_version, dispatch_subject, trace_id, idempotency_key,
                isolation_tier, status, lease_epoch, accept_deadline, soft_deadline,
                hard_deadline, accepted_at, last_progress_seq, last_heartbeat_seq,
                last_heartbeat_at, cancellation_reason, cancellation_requested_at,
                completed_at, failed_at, failure_error_code, failure_error_class, retryable,
                safe_to_retry, compensation_possible, uncertain_side_effect, result_artifact_id,
                normalized_result, last_payload, inserted_at, updated_at
      """,
      [
        execution_id,
        merged.worker_kind,
        Map.get(merged, :worker_id),
        merged.contract_version,
        merged.dispatch_subject,
        Map.get(merged, :trace_id),
        Map.get(merged, :idempotency_key),
        merged.isolation_tier,
        merged.status,
        merged.lease_epoch,
        parse_datetime(Map.get(merged, :accept_deadline)),
        parse_datetime(Map.get(merged, :soft_deadline)),
        parse_datetime(Map.get(merged, :hard_deadline)),
        parse_datetime(Map.get(merged, :accepted_at)),
        Map.get(merged, :last_progress_seq, 0),
        Map.get(merged, :last_heartbeat_seq, 0),
        parse_datetime(Map.get(merged, :last_heartbeat_at)),
        Map.get(merged, :cancellation_reason),
        parse_datetime(Map.get(merged, :cancellation_requested_at)),
        parse_datetime(Map.get(merged, :completed_at)),
        parse_datetime(Map.get(merged, :failed_at)),
        Map.get(merged, :failure_error_code),
        Map.get(merged, :failure_error_class),
        Map.get(merged, :retryable),
        Map.get(merged, :safe_to_retry),
        Map.get(merged, :compensation_possible),
        Map.get(merged, :uncertain_side_effect, false),
        Map.get(merged, :result_artifact_id),
        Map.get(merged, :normalized_result),
        Map.get(merged, :last_payload, %{}),
        merged.updated_at
      ]
    )
    |> rows_to_maps()
    |> List.first()
    |> normalize_map()
  end

  defp rows_to_maps(%{columns: columns, rows: rows}) do
    Enum.map(rows, fn row ->
      columns
      |> Enum.zip(row)
      |> Enum.into(%{})
      |> normalize_map()
    end)
  end

  defp normalize_map(%_{} = value), do: value

  defp normalize_map(value) when is_map(value) do
    value
    |> Enum.map(fn {key, item} -> {normalize_key(key), normalize_map(item)} end)
    |> Enum.into(%{})
  end

  defp normalize_map(value) when is_list(value), do: Enum.map(value, &normalize_map/1)
  defp normalize_map(value), do: value

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

  defp parse_datetime(nil), do: nil
  defp parse_datetime(%DateTime{} = value), do: value

  defp parse_datetime(value) when is_binary(value) do
    {:ok, parsed, _offset} = DateTime.from_iso8601(value)
    parsed
  end

  defp unwrap_transaction({:ok, value}), do: value
  defp unwrap_transaction({:error, reason}), do: raise("transaction failed: #{inspect(reason)}")

  defp now, do: DateTime.utc_now() |> DateTime.truncate(:second)
end
