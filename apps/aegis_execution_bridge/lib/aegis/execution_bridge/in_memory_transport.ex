defmodule Aegis.ExecutionBridge.InMemoryTransport do
  @moduledoc """
  Deterministic in-memory transport adapter used by the Phase 04 test harness.

  The boundary is shaped like a transport adapter so a real JetStream client can
  replace it later without changing bridge semantics.
  """

  use GenServer

  def start_link(_init_arg \\ []) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def subscribe(consumer_name, subject_pattern, pid, opts \\ [])
      when is_binary(subject_pattern) and is_pid(pid) do
    GenServer.call(
      __MODULE__,
      {:subscribe, to_string(consumer_name), subject_pattern, pid, Enum.into(opts, %{})}
    )
  end

  def publish(subject, payload, headers)
      when is_binary(subject) and is_map(payload) and is_map(headers) do
    GenServer.call(__MODULE__, {:publish, subject, payload, headers})
  end

  def published_messages do
    GenServer.call(__MODULE__, :published_messages)
  end

  def reset! do
    GenServer.call(__MODULE__, :reset)
  end

  @impl true
  def init(_state), do: {:ok, %{next_message_id: 1, published_messages: [], subscriptions: []}}

  @impl true
  def handle_call({:subscribe, consumer_name, subject_pattern, pid, opts}, _from, state) do
    subscription = %{
      consumer_name: consumer_name,
      subject_pattern: subject_pattern,
      pid: pid,
      max_deliver: Map.get(opts, :max_deliver, 1)
    }

    subscriptions =
      state.subscriptions
      |> Enum.reject(
        &(&1.consumer_name == consumer_name and &1.subject_pattern == subject_pattern)
      )
      |> Kernel.++([subscription])

    {:reply, :ok, %{state | subscriptions: subscriptions}}
  end

  @impl true
  def handle_call({:publish, subject, payload, headers}, _from, state) do
    base_message = %{
      message_id: "msg-#{state.next_message_id}",
      subject: subject,
      payload: payload,
      headers: headers,
      published_at: DateTime.utc_now() |> DateTime.truncate(:second),
      deliveries: [],
      ack_status: :unconsumed,
      error: nil
    }

    matching_subscriptions =
      Enum.filter(state.subscriptions, &matches_subject?(&1.subject_pattern, subject))

    message =
      case matching_subscriptions do
        [] ->
          base_message

        subscriptions ->
          Enum.reduce(subscriptions, base_message, &deliver_to_subscriber(&2, &1))
      end

    next_state = %{
      state
      | next_message_id: state.next_message_id + 1,
        published_messages: state.published_messages ++ [message]
    }

    case message.ack_status do
      :max_deliver_exceeded -> {:reply, {:error, message.error, message}, next_state}
      _other -> {:reply, {:ok, message}, next_state}
    end
  end

  def handle_call(:published_messages, _from, state) do
    {:reply, state.published_messages, state}
  end

  def handle_call(:reset, _from, state) do
    {:reply, :ok, %{state | next_message_id: 1, published_messages: []}}
  end

  defp deliver_to_subscriber(message, subscription) do
    1..subscription.max_deliver
    |> Enum.reduce_while(message, fn attempt, acc ->
      delivery = %{
        consumer_name: subscription.consumer_name,
        subject_pattern: subscription.subject_pattern,
        attempt: attempt
      }

      case deliver(subscription.pid, acc, delivery) do
        {:ack, result} ->
          next_message =
            acc
            |> append_delivery(Map.put(delivery, :status, :ack))
            |> Map.put(:ack_status, :ack)
            |> Map.put(:error, nil)
            |> maybe_put_result(result)

          {:halt, next_message}

        {:nack, reason} when attempt < subscription.max_deliver ->
          next_message =
            acc
            |> append_delivery(Map.put(delivery, :status, :nack))
            |> Map.put(:ack_status, :nack)
            |> Map.put(:error, reason)

          {:cont, next_message}

        {:nack, reason} ->
          next_message =
            acc
            |> append_delivery(Map.put(delivery, :status, :nack))
            |> Map.put(:ack_status, :max_deliver_exceeded)
            |> Map.put(:error, reason)

          {:halt, next_message}
      end
    end)
  end

  defp deliver(pid, message, delivery) do
    transport_message =
      message
      |> Map.put(:delivery_attempt, delivery.attempt)
      |> Map.put(:consumer_name, delivery.consumer_name)

    try do
      case GenServer.call(pid, {:transport_message, transport_message}, 5_000) do
        :ack -> {:ack, nil}
        {:ack, result} -> {:ack, result}
        {:nack, reason} -> {:nack, reason}
      end
    catch
      :exit, reason -> {:nack, {:consumer_exit, reason}}
    end
  end

  defp append_delivery(message, delivery) do
    Map.update!(message, :deliveries, &(&1 ++ [delivery]))
  end

  defp maybe_put_result(message, nil), do: message
  defp maybe_put_result(message, result), do: Map.put(message, :consumer_result, result)

  defp matches_subject?(pattern, subject) do
    Aegis.ExecutionBridge.TransportTopology.matches_subject?(pattern, subject)
  end
end
