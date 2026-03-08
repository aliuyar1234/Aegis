defmodule Aegis.Leases.SessionLease do
  @moduledoc false

  @type status :: :active | :ambiguous | :expired

  @enforce_keys [
    :session_id,
    :tenant_id,
    :workspace_id,
    :owner_node,
    :lease_epoch,
    :lease_status,
    :lease_expires_at,
    :last_renewed_at,
    :inserted_at,
    :updated_at
  ]
  defstruct [
    :session_id,
    :tenant_id,
    :workspace_id,
    :owner_node,
    :lease_epoch,
    :lease_status,
    :lease_expires_at,
    :last_renewed_at,
    :recovery_reason,
    :inserted_at,
    :updated_at
  ]

  @type t :: %__MODULE__{
          session_id: String.t(),
          tenant_id: String.t(),
          workspace_id: String.t(),
          owner_node: String.t(),
          lease_epoch: pos_integer(),
          lease_status: status(),
          lease_expires_at: DateTime.t(),
          last_renewed_at: DateTime.t(),
          recovery_reason: String.t() | nil,
          inserted_at: DateTime.t(),
          updated_at: DateTime.t()
        }
end
