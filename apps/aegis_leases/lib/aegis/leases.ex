defmodule Aegis.Leases do
  @moduledoc """
  Postgres-backed lease authority for exactly-one-owner session execution.

  `aegis_runtime` may cache owner metadata inside the `SessionKernel`, but lease
  authority lives here and is validated against PostgreSQL before commands can
  advance authoritative state.
  """

  alias Aegis.Leases.SessionLease
  alias Aegis.Repo
  alias Ecto.Adapters.SQL

  @default_lease_ttl_seconds 30

  @type authorize_error ::
          :missing_lease
          | {:lease_not_authoritative, SessionLease.status(), SessionLease.t()}
          | {:lease_owner_mismatch, String.t(), SessionLease.t()}
          | {:stale_lease_epoch, non_neg_integer(), pos_integer()}
          | {:lease_still_active, SessionLease.t()}

  @spec claim(map() | keyword(), keyword()) :: {:ok, SessionLease.t()} | {:error, term()}
  def claim(session_attrs, opts \\ []) do
    attrs = normalize_attrs(session_attrs)
    owner_node = Keyword.get(opts, :owner_node, Map.get(attrs, :owner_node, Atom.to_string(node())))
    lease_epoch = max(Map.get(attrs, :lease_epoch, 0), 1)
    now = now()

    Repo.transaction(fn ->
      case lock_lease(attrs.session_id) do
        nil ->
          insert_lease!(%{
            session_id: attrs.session_id,
            tenant_id: attrs.tenant_id,
            workspace_id: attrs.workspace_id,
            owner_node: owner_node,
            lease_epoch: lease_epoch,
            lease_status: :active,
            lease_expires_at: expires_at(now),
            last_renewed_at: now,
            recovery_reason: nil,
            inserted_at: now,
            updated_at: now
          })

        lease ->
          lease = expire_if_elapsed!(lease, now)

          if lease.owner_node == owner_node and lease.lease_status == :active do
            renew_locked!(lease, now)
          else
            lease
          end
      end
    end)
    |> unwrap_transaction()
  end

  @spec current(String.t()) :: {:ok, SessionLease.t()} | {:error, :missing_lease}
  def current(session_id) when is_binary(session_id) do
    case fetch_lease(session_id) do
      nil -> {:error, :missing_lease}
      lease -> {:ok, lease}
    end
  end

  @spec authorize_command(String.t(), keyword()) ::
          {:ok, SessionLease.t()} | {:error, authorize_error()}
  def authorize_command(session_id, opts \\ []) when is_binary(session_id) do
    now = now()
    expected_owner = Keyword.get(opts, :owner_node)
    expected_epoch = Keyword.get(opts, :lease_epoch)

    Repo.transaction(fn ->
      lease =
        session_id
        |> lock_lease()
        |> case do
          nil -> Repo.rollback(:missing_lease)
          locked -> expire_if_elapsed!(locked, now)
        end

      cond do
        lease.lease_status != :active ->
          Repo.rollback({:lease_not_authoritative, lease.lease_status, lease})

        expected_owner && expected_owner != lease.owner_node ->
          Repo.rollback({:lease_owner_mismatch, expected_owner, lease})

        expected_epoch != nil && expected_epoch != lease.lease_epoch ->
          Repo.rollback({:stale_lease_epoch, expected_epoch, lease.lease_epoch})

        true ->
          renew_locked!(lease, now)
      end
    end)
    |> unwrap_transaction()
  end

  @spec adopt(String.t(), map() | keyword(), keyword()) ::
          {:ok, SessionLease.t()} | {:error, authorize_error()}
  def adopt(session_id, attrs, opts \\ []) when is_binary(session_id) do
    attrs = normalize_attrs(attrs)
    owner_node = Keyword.get(opts, :owner_node, Map.get(attrs, :owner_node, Atom.to_string(node())))
    now = now()

    Repo.transaction(fn ->
      case lock_lease(session_id) do
        nil ->
          insert_lease!(%{
            session_id: session_id,
            tenant_id: Map.fetch!(attrs, :tenant_id),
            workspace_id: Map.fetch!(attrs, :workspace_id),
            owner_node: owner_node,
            lease_epoch: max(Map.get(attrs, :lease_epoch, 0), 0) + 1,
            lease_status: :active,
            lease_expires_at: expires_at(now),
            last_renewed_at: now,
            recovery_reason: Map.get(attrs, :recovery_reason),
            inserted_at: now,
            updated_at: now
          })

        lease ->
          lease = expire_if_elapsed!(lease, now)

          if lease.lease_status == :active do
            Repo.rollback({:lease_still_active, lease})
          else
            update_lease!(
              session_id,
              owner_node,
              lease.lease_epoch + 1,
              :active,
              expires_at(now),
              now,
              Map.get(attrs, :recovery_reason)
            )
          end
      end
    end)
    |> unwrap_transaction()
  end

  @spec mark_ambiguous(String.t(), map() | keyword()) ::
          {:ok, SessionLease.t()} | {:error, authorize_error()}
  def mark_ambiguous(session_id, attrs) when is_binary(session_id) do
    attrs = normalize_attrs(attrs)
    now = now()
    expected_owner = Map.get(attrs, :owner_node)
    expected_epoch = Map.get(attrs, :lease_epoch)
    recovery_reason = Map.get(attrs, :reason, "lease_ambiguity")

    Repo.transaction(fn ->
      lease =
        session_id
        |> lock_lease()
        |> case do
          nil -> Repo.rollback(:missing_lease)
          locked -> expire_if_elapsed!(locked, now)
        end

      cond do
        expected_owner && expected_owner != lease.owner_node ->
          Repo.rollback({:lease_owner_mismatch, expected_owner, lease})

        expected_epoch != nil && expected_epoch != lease.lease_epoch ->
          Repo.rollback({:stale_lease_epoch, expected_epoch, lease.lease_epoch})

        true ->
          update_lease!(
            session_id,
            lease.owner_node,
            lease.lease_epoch,
            :ambiguous,
            now,
            now,
            recovery_reason
          )
      end
    end)
    |> unwrap_transaction()
  end

  @spec lease_ttl_seconds() :: pos_integer()
  def lease_ttl_seconds do
    Application.get_env(:aegis_leases, :lease_ttl_seconds, @default_lease_ttl_seconds)
  end

  defp fetch_lease(session_id) do
    SQL.query!(
      Repo,
      """
      SELECT session_id, tenant_id, workspace_id, owner_node, lease_epoch, lease_status,
             lease_expires_at, last_renewed_at, recovery_reason, inserted_at, updated_at
      FROM session_leases
      WHERE session_id = $1
      """,
      [session_id]
    )
    |> rows_to_maps()
    |> List.first()
    |> normalize_lease()
  end

  defp lock_lease(session_id) do
    SQL.query!(
      Repo,
      """
      SELECT session_id, tenant_id, workspace_id, owner_node, lease_epoch, lease_status,
             lease_expires_at, last_renewed_at, recovery_reason, inserted_at, updated_at
      FROM session_leases
      WHERE session_id = $1
      FOR UPDATE
      """,
      [session_id]
    )
    |> rows_to_maps()
    |> List.first()
    |> normalize_lease()
  end

  defp insert_lease!(attrs) do
    SQL.query!(
      Repo,
      """
      INSERT INTO session_leases (
        session_id, tenant_id, workspace_id, owner_node, lease_epoch, lease_status,
        lease_expires_at, last_renewed_at, recovery_reason, inserted_at, updated_at
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
      RETURNING session_id, tenant_id, workspace_id, owner_node, lease_epoch, lease_status,
                lease_expires_at, last_renewed_at, recovery_reason, inserted_at, updated_at
      """,
      [
        attrs.session_id,
        attrs.tenant_id,
        attrs.workspace_id,
        attrs.owner_node,
        attrs.lease_epoch,
        Atom.to_string(attrs.lease_status),
        attrs.lease_expires_at,
        attrs.last_renewed_at,
        attrs.recovery_reason,
        attrs.inserted_at,
        attrs.updated_at
      ]
    )
    |> rows_to_maps()
    |> List.first()
    |> normalize_lease()
  end

  defp renew_locked!(lease, now) do
    update_lease!(
      lease.session_id,
      lease.owner_node,
      lease.lease_epoch,
      :active,
      expires_at(now),
      now,
      nil
    )
  end

  defp update_lease!(session_id, owner_node, lease_epoch, lease_status, lease_expires_at, now, recovery_reason) do
    SQL.query!(
      Repo,
      """
      UPDATE session_leases
      SET owner_node = $2,
          lease_epoch = $3,
          lease_status = $4,
          lease_expires_at = $5,
          last_renewed_at = $6,
          recovery_reason = $7,
          updated_at = $6
      WHERE session_id = $1
      RETURNING session_id, tenant_id, workspace_id, owner_node, lease_epoch, lease_status,
                lease_expires_at, last_renewed_at, recovery_reason, inserted_at, updated_at
      """,
      [
        session_id,
        owner_node,
        lease_epoch,
        Atom.to_string(lease_status),
        lease_expires_at,
        now,
        recovery_reason
      ]
    )
    |> rows_to_maps()
    |> List.first()
    |> normalize_lease()
  end

  defp expire_if_elapsed!(lease, reference_now) do
    if lease.lease_status == :active and DateTime.compare(lease.lease_expires_at, reference_now) != :gt do
      update_lease!(
        lease.session_id,
        lease.owner_node,
        lease.lease_epoch,
        :expired,
        lease.lease_expires_at,
        lease.last_renewed_at,
        lease.recovery_reason || "lease_expired"
      )
    else
      lease
    end
  end

  defp rows_to_maps(%{columns: columns, rows: rows}) do
    Enum.map(rows, fn row ->
      columns
      |> Enum.zip(row)
      |> Enum.into(%{})
      |> normalize_map()
    end)
  end

  defp normalize_lease(nil), do: nil

  defp normalize_lease(row) do
    %SessionLease{
      session_id: row.session_id,
      tenant_id: row.tenant_id,
      workspace_id: row.workspace_id,
      owner_node: row.owner_node,
      lease_epoch: row.lease_epoch,
      lease_status: normalize_status(row.lease_status, row.lease_expires_at),
      lease_expires_at: row.lease_expires_at,
      last_renewed_at: row.last_renewed_at,
      recovery_reason: row.recovery_reason,
      inserted_at: row.inserted_at,
      updated_at: row.updated_at
    }
  end

  defp normalize_status("active", lease_expires_at) do
    if DateTime.compare(lease_expires_at, now()) == :gt, do: :active, else: :expired
  end

  defp normalize_status(status, _lease_expires_at) when is_binary(status), do: String.to_existing_atom(status)
  defp normalize_status(status, _lease_expires_at) when is_atom(status), do: status

  defp normalize_attrs(attrs) do
    attrs
    |> to_map()
    |> normalize_map()
  end

  defp to_map(%{__struct__: _} = value), do: Map.from_struct(value)
  defp to_map(value) when is_map(value), do: value
  defp to_map(value), do: Map.new(value)

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

  defp expires_at(reference_now), do: DateTime.add(reference_now, lease_ttl_seconds(), :second)

  defp unwrap_transaction({:ok, value}), do: {:ok, value}
  defp unwrap_transaction({:error, reason}), do: {:error, reason}

  defp now, do: DateTime.utc_now() |> DateTime.truncate(:second)
end
