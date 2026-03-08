defmodule Aegis.ExecutionBridge.TransportTopology do
  @moduledoc """
  Convenience wrapper around the generated Phase 04 transport topology manifest.
  """

  alias Aegis.ExecutionBridge.Generated.Contracts

  @default_timeout_class "medium"

  def headers, do: Contracts.transport_topology()["headers"]
  def source_digest, do: Contracts.source_digest()
  def message_names, do: Contracts.message_names()
  def consumers, do: Contracts.transport_topology()["consumers"]

  def subjects do
    Contracts.transport_topology()["subjects"]
  end

  def subject(name) when is_atom(name), do: subject(Atom.to_string(name))

  def subject(name) when is_binary(name) do
    subjects()
    |> Enum.find(&(Map.fetch!(&1, "name") == name))
    |> case do
      nil -> raise ArgumentError, "unknown transport subject #{inspect(name)}"
      entry -> entry
    end
  end

  def consumer(name) when is_atom(name), do: consumer(Atom.to_string(name))

  def consumer(name) when is_binary(name) do
    consumers()
    |> Enum.find(&(Map.fetch!(&1, "name") == name))
    |> case do
      nil -> raise ArgumentError, "unknown transport consumer #{inspect(name)}"
      entry -> entry
    end
  end

  def subject_for(name, worker_kind) do
    subject(name)
    |> Map.fetch!("subject")
    |> String.replace("{worker_kind}", worker_kind)
  end

  def routed_subject_for(name, worker_kind, route_key)
      when is_atom(name) and is_binary(worker_kind) do
    base_subject = subject_for(name, worker_kind)

    case normalize_route_key(route_key) do
      "shared" -> base_subject
      route_key -> base_subject <> "." <> route_key
    end
  end

  def timeout_class(timeout_class) do
    timeout_class =
      case timeout_class do
        "standard" -> @default_timeout_class
        nil -> @default_timeout_class
        other -> other
      end

    Contracts.transport_topology()
    |> get_in(["policies", "timeout_classes", timeout_class])
    |> case do
      nil -> raise ArgumentError, "unknown timeout class #{inspect(timeout_class)}"
      encoded -> decode_timeout_policy(timeout_class, encoded)
    end
  end

  def heartbeat_expectation do
    Contracts.transport_topology()
    |> get_in(["policies", "heartbeat_expectation"])
    |> then(fn policy ->
      %{
        default_interval_seconds: duration_to_seconds(Map.fetch!(policy, "default_interval")),
        missed_heartbeats_before_loss: Map.fetch!(policy, "missed_heartbeats_before_loss")
      }
    end)
  end

  def matches_subject?(pattern, subject) when is_binary(pattern) and is_binary(subject) do
    pattern_segments = String.split(pattern, ".")
    subject_segments = String.split(subject, ".")
    do_matches_subject?(pattern_segments, subject_segments)
  end

  def max_deliver_for_consumer(name) do
    consumer(name)
    |> Map.fetch!("max_deliver")
  end

  def max_deliver_for_subject(subject) do
    consumers()
    |> Enum.filter(&matches_subject?(Map.fetch!(&1, "filter_subject"), subject))
    |> Enum.map(&Map.fetch!(&1, "max_deliver"))
    |> Enum.max(fn -> 1 end)
  end

  defp decode_timeout_policy(timeout_class, encoded) do
    parts =
      encoded
      |> String.split(",")
      |> Enum.map(&String.trim/1)
      |> Enum.map(fn segment ->
        [name, value] = String.split(segment, "<=", parts: 2)
        {String.trim(name), duration_to_seconds(String.trim(value))}
      end)
      |> Enum.into(%{})

    %{
      timeout_class: timeout_class,
      accept_seconds: Map.fetch!(parts, "accept"),
      soft_seconds: Map.fetch!(parts, "soft"),
      hard_seconds: Map.fetch!(parts, "hard")
    }
  end

  defp duration_to_seconds(value) do
    case Regex.run(~r/\A(\d+)(s|m|h)\z/, value) do
      [_, amount, "s"] -> String.to_integer(amount)
      [_, amount, "m"] -> String.to_integer(amount) * 60
      [_, amount, "h"] -> String.to_integer(amount) * 3600
      _ -> raise ArgumentError, "unsupported duration #{inspect(value)}"
    end
  end

  defp do_matches_subject?([], []), do: true
  defp do_matches_subject?([">"], _subject_segments), do: true
  defp do_matches_subject?([], _subject_segments), do: false
  defp do_matches_subject?(_pattern_segments, []), do: false

  defp do_matches_subject?(["*" | pattern_tail], [_segment | subject_tail]),
    do: do_matches_subject?(pattern_tail, subject_tail)

  defp do_matches_subject?([pattern_head | pattern_tail], [subject_head | subject_tail]) do
    pattern_head == subject_head and do_matches_subject?(pattern_tail, subject_tail)
  end

  defp normalize_route_key(nil), do: "shared"
  defp normalize_route_key(""), do: "shared"
  defp normalize_route_key(route_key), do: route_key
end
