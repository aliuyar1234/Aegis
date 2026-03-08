defmodule Aegis.ExecutionBridge.TransportConsumer do
  @moduledoc false

  use GenServer

  alias Aegis.ExecutionBridge.{InMemoryTransport, TransportTopology}

  def start_link(_opts \\ []) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  @impl true
  def init(state) do
    subscribe!("runtime-worker-registry")
    subscribe!("runtime-worker-events")
    {:ok, state}
  end

  @impl true
  def handle_call({:transport_message, message}, _from, state) do
    reply =
      case consume(message) do
        {:ok, result} -> {:ack, result}
        :ok -> :ack
        {:error, reason} -> {:nack, reason}
      end

    {:reply, reply, state}
  end

  defp subscribe!(consumer_name) do
    consumer = TransportTopology.consumer(consumer_name)

    InMemoryTransport.subscribe(
      consumer_name,
      Map.fetch!(consumer, "filter_subject"),
      self(),
      max_deliver: Map.fetch!(consumer, "max_deliver")
    )
  end

  defp consume(message) do
    case subject_name(message.subject) do
      {:worker_register, _worker_kind} ->
        Aegis.ExecutionBridge.process_worker_registration(message.payload)

      {:worker_heartbeat, _worker_kind} ->
        Aegis.ExecutionBridge.process_worker_heartbeat(message.payload)

      {kind, worker_kind}
      when kind in [:accepted, :progress, :heartbeat, :completed, :failed, :cancelled] ->
        Aegis.ExecutionBridge.process_worker_callback(
          kind,
          worker_kind,
          message.payload,
          message.headers
        )

      :unknown ->
        {:error, {:unknown_transport_subject, message.subject}}
    end
  end

  defp subject_name(subject) do
    worker_kind = subject |> String.split(".") |> List.last()

    cond do
      String.starts_with?(subject, "aegis.v1.registry.register.") ->
        {:worker_register, worker_kind}

      String.starts_with?(subject, "aegis.v1.registry.heartbeat.") ->
        {:worker_heartbeat, worker_kind}

      String.starts_with?(subject, "aegis.v1.event.accepted.") ->
        {:accepted, worker_kind}

      String.starts_with?(subject, "aegis.v1.event.progress.") ->
        {:progress, worker_kind}

      String.starts_with?(subject, "aegis.v1.event.heartbeat.") ->
        {:heartbeat, worker_kind}

      String.starts_with?(subject, "aegis.v1.event.completed.") ->
        {:completed, worker_kind}

      String.starts_with?(subject, "aegis.v1.event.failed.") ->
        {:failed, worker_kind}

      String.starts_with?(subject, "aegis.v1.event.cancelled.") ->
        {:cancelled, worker_kind}

      true ->
        :unknown
    end
  end
end
