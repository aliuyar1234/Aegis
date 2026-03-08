defmodule Aegis.Events.Checkpoint do
  @moduledoc """
  Stored structured checkpoint row.
  """

  @enforce_keys [:checkpoint_id, :session_id, :seq_no, :payload, :inserted_at]
  defstruct [:checkpoint_id, :session_id, :seq_no, :payload, :inserted_at]

  @type t :: %__MODULE__{
          checkpoint_id: String.t(),
          session_id: String.t(),
          seq_no: non_neg_integer(),
          payload: map(),
          inserted_at: DateTime.t()
        }
end
