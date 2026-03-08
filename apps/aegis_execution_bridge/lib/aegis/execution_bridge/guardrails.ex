defmodule Aegis.ExecutionBridge.Guardrails do
  @moduledoc """
  Explicit write-boundary guardrails for execution-plane code.

  Workers and worker-facing adapters may never write canonical control-plane
  tables. The bridge only writes its own transport-facing tables.
  """

  @forbidden_tables MapSet.new([
                      "sessions",
                      "session_events",
                      "session_checkpoints",
                      "session_leases",
                      "approvals",
                      "outbox"
                    ])
  @allowed_tables MapSet.new(["action_executions", "worker_registrations"])

  def forbidden_tables, do: MapSet.to_list(@forbidden_tables) |> Enum.sort()
  def allowed_tables, do: MapSet.to_list(@allowed_tables) |> Enum.sort()

  def assert_write_allowed!(table) when is_binary(table) do
    cond do
      MapSet.member?(@allowed_tables, table) ->
        :ok

      MapSet.member?(@forbidden_tables, table) ->
        raise ArgumentError, "execution bridge may not write canonical table #{inspect(table)}"

      true ->
        raise ArgumentError, "unknown or unapproved execution bridge table #{inspect(table)}"
    end
  end
end
