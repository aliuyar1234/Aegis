defmodule Aegis.ExecutionBridge.Poller do
  @moduledoc false

  use GenServer

  def start_link(opts) do
    name = Keyword.fetch!(opts, :name)
    GenServer.start_link(__MODULE__, Map.new(opts), name: name)
  end

  @impl true
  def init(%{interval_ms: interval_ms} = state) do
    schedule(interval_ms)
    {:ok, state}
  end

  @impl true
  def handle_info(:tick, state) do
    run(state.action)
    schedule(state.interval_ms)
    {:noreply, state}
  end

  defp run(:dispatch), do: Aegis.ExecutionBridge.flush_dispatches()
  defp run(:timeouts), do: Aegis.ExecutionBridge.scan_timeouts()

  defp schedule(interval_ms) when interval_ms in [:manual, nil, false, 0], do: :ok

  defp schedule(interval_ms) when is_integer(interval_ms) and interval_ms > 0,
    do: Process.send_after(self(), :tick, interval_ms)
end
