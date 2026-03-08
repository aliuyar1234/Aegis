defmodule Aegis.Runtime.SessionHostSupervisor do
  @moduledoc """
  Dynamic host supervisor for authoritative per-session runtime trees.

  This is the only place in Phase 01 that starts new session trees.
  Each child tree contains one authoritative `SessionKernel` plus the ephemeral
  helper processes defined by the locked runtime model.
  """

  use DynamicSupervisor

  alias Aegis.Runtime.SessionTreeSupervisor

  def start_link(init_arg \\ []) do
    DynamicSupervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg), do: DynamicSupervisor.init(strategy: :one_for_one)

  @spec start_session(map() | keyword()) :: DynamicSupervisor.on_start_child()
  def start_session(attrs) do
    DynamicSupervisor.start_child(__MODULE__, {SessionTreeSupervisor, attrs})
  end
end
