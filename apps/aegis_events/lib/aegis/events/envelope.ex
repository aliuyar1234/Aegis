defmodule Aegis.Events.Envelope do
  @moduledoc """
  Durable event envelope used by the Phase 02 store and replay engine.
  """

  @enforce_keys [
    :event_id,
    :tenant_id,
    :workspace_id,
    :session_id,
    :seq_no,
    :type,
    :event_version,
    :occurred_at,
    :recorded_at,
    :actor_kind,
    :actor_id,
    :lease_epoch,
    :determinism_class,
    :prev_event_hash,
    :event_hash,
    :payload
  ]
  defstruct [
    :event_id,
    :tenant_id,
    :workspace_id,
    :session_id,
    :seq_no,
    :type,
    :event_version,
    :occurred_at,
    :recorded_at,
    :actor_kind,
    :actor_id,
    :command_id,
    :correlation_id,
    :causation_id,
    :trace_id,
    :span_id,
    :lease_epoch,
    :idempotency_key,
    :determinism_class,
    :prev_event_hash,
    :event_hash,
    :payload
  ]

  @type t :: %__MODULE__{
          event_id: String.t(),
          tenant_id: String.t(),
          workspace_id: String.t(),
          session_id: String.t(),
          seq_no: non_neg_integer(),
          type: String.t(),
          event_version: non_neg_integer(),
          occurred_at: DateTime.t(),
          recorded_at: DateTime.t(),
          actor_kind: String.t(),
          actor_id: String.t(),
          command_id: String.t() | nil,
          correlation_id: String.t() | nil,
          causation_id: String.t() | nil,
          trace_id: String.t() | nil,
          span_id: String.t() | nil,
          lease_epoch: non_neg_integer(),
          idempotency_key: String.t() | nil,
          determinism_class: String.t(),
          prev_event_hash: String.t(),
          event_hash: String.t(),
          payload: map()
        }
end
