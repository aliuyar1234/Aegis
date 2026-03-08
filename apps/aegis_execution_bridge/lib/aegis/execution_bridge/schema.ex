defmodule Aegis.ExecutionBridge.Schema do
  @moduledoc """
  Durable Phase 04 transport-facing tables owned by `aegis_execution_bridge`.
  """

  @tables [
    %{name: "worker_registrations", purpose: "durable registry and liveness view for workers"},
    %{name: "action_executions", purpose: "transport attempt state for accepted and in-flight executions"}
  ]

  def tables, do: @tables
end
