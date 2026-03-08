defmodule Aegis.Events.Schema do
  @moduledoc """
  Canonical Postgres table layout for the Phase 02 event store.
  """

  @tables [
    %{name: "sessions", purpose: "session identity and latest durable pointers"},
    %{name: "session_events", purpose: "append-only per-session timeline"},
    %{name: "session_checkpoints", purpose: "structured checkpoints for hydrate replay"},
    %{name: "outbox", purpose: "committed intent for downstream dispatch"}
  ]

  def tables, do: @tables
end
