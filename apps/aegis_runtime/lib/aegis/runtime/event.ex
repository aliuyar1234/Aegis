defmodule Aegis.Runtime.Event do
  @moduledoc """
  Lightweight event envelope produced by `Aegis.Runtime.CommandHandler`.

  `SessionKernel` turns these envelopes into durable event-store writes through
  `Aegis.Events`.
  """

  @enforce_keys [:seq_no, :type, :payload, :recorded_at]
  defstruct [
    :seq_no,
    :type,
    :payload,
    :recorded_at,
    :command_id,
    :correlation_id,
    :causation_id,
    :trace_id,
    :span_id,
    :idempotency_key
  ]

  @type t :: %__MODULE__{
          seq_no: non_neg_integer(),
          type: String.t(),
          payload: map(),
          recorded_at: DateTime.t(),
          command_id: String.t() | nil,
          correlation_id: String.t() | nil,
          causation_id: String.t() | nil,
          trace_id: String.t() | nil,
          span_id: String.t() | nil,
          idempotency_key: String.t() | nil
        }

  @spec new(non_neg_integer(), String.t(), map(), map()) :: t()
  def new(seq_no, type, payload, metadata \\ %{})
      when is_integer(seq_no) and is_binary(type) and is_map(payload) do
    metadata = Map.new(metadata)

    %__MODULE__{
      seq_no: seq_no,
      type: type,
      payload: payload,
      recorded_at: DateTime.utc_now() |> DateTime.truncate(:second),
      command_id: Map.get(metadata, :command_id),
      correlation_id: Map.get(metadata, :correlation_id),
      causation_id: Map.get(metadata, :causation_id),
      trace_id: Map.get(metadata, :trace_id),
      span_id: Map.get(metadata, :span_id),
      idempotency_key: Map.get(metadata, :idempotency_key)
    }
  end
end
