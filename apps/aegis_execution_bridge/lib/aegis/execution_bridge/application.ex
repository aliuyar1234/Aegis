defmodule Aegis.ExecutionBridge.Application do
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    config = Application.get_env(:aegis, Aegis.ExecutionBridge, [])

    children = [
      Aegis.ExecutionBridge.InMemoryTransport,
      Aegis.ExecutionBridge.TransportConsumer,
      Supervisor.child_spec(
        {Aegis.ExecutionBridge.Poller,
         name: Aegis.ExecutionBridge.DispatchPoller,
         action: :dispatch,
         interval_ms: Keyword.get(config, :dispatch_poll_interval_ms, 100)},
        id: Aegis.ExecutionBridge.DispatchPoller
      ),
      Supervisor.child_spec(
        {Aegis.ExecutionBridge.Poller,
         name: Aegis.ExecutionBridge.TimeoutPoller,
         action: :timeouts,
         interval_ms: Keyword.get(config, :timeout_poll_interval_ms, 1_000)},
        id: Aegis.ExecutionBridge.TimeoutPoller
      )
    ]

    Supervisor.start_link(children, strategy: :one_for_one, name: __MODULE__)
  end
end
