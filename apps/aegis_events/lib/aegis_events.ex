defmodule AegisEvents do
  @moduledoc """
  Compatibility wrapper for the `aegis_events` umbrella application.

  The Phase 02 implementation lives under `Aegis.Events`.
  """

  defdelegate reset!(), to: Aegis.Events
  defdelegate append(session_state, events, opts \\ []), to: Aegis.Events
  defdelegate sessions(scope \\ %{}), to: Aegis.Events
  defdelegate session_exists?(session_id, scope \\ %{}), to: Aegis.Events
  defdelegate live_session_count(scope \\ %{}), to: Aegis.Events
  defdelegate events(session_id, scope \\ %{}), to: Aegis.Events
  defdelegate latest_checkpoint(session_id, scope \\ %{}), to: Aegis.Events
  defdelegate checkpoints(session_id, scope \\ %{}), to: Aegis.Events
  defdelegate outbox(session_id, scope \\ %{}), to: Aegis.Events
  defdelegate historical_replay(session_id, scope \\ %{}), to: Aegis.Events
  defdelegate replay_at(session_id, seq_no, scope \\ %{}), to: Aegis.Events
  defdelegate hydrate(session_id, scope \\ %{}), to: Aegis.Events
  defdelegate schema_tables(), to: Aegis.Events
end
