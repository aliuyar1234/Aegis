defmodule Aegis.Policy.QuotaPolicy do
  @moduledoc """
  Phase 09 quota policy lookup for scoped admission control.

  The limits are intentionally conservative defaults and can be overridden with
  `config :aegis_policy, :quota_limits, ...` in deployment or tests.
  """

  @default_limits %{
    "tier_a" => %{
      live_sessions: 25,
      concurrent_browser_contexts: 4,
      concurrent_effectful_actions: 2
    },
    "tier_b" => %{
      live_sessions: 100,
      concurrent_browser_contexts: 16,
      concurrent_effectful_actions: 8
    },
    "tier_c" => %{
      live_sessions: 500,
      concurrent_browser_contexts: 64,
      concurrent_effectful_actions: 32
    }
  }

  @type quota_class :: :live_sessions | :concurrent_browser_contexts | :concurrent_effectful_actions

  @spec limit_for(quota_class(), map() | keyword()) :: non_neg_integer()
  def limit_for(quota_class, attrs) when quota_class in [:live_sessions, :concurrent_browser_contexts, :concurrent_effectful_actions] do
    attrs = normalize_map(attrs)
    tier = isolation_tier(attrs)

    Application.get_env(:aegis_policy, :quota_limits, @default_limits)
    |> normalize_limits()
    |> Map.get(tier, @default_limits["tier_a"])
    |> Map.fetch!(quota_class)
  end

  @spec isolation_tier(map() | keyword()) :: String.t()
  def isolation_tier(attrs) do
    attrs
    |> normalize_map()
    |> Map.get(:isolation_tier, "tier_a")
    |> to_string()
  end

  defp normalize_limits(raw_limits) when is_map(raw_limits) do
    raw_limits
    |> Enum.map(fn {tier, limits} ->
      {to_string(tier), normalize_limit_bucket(limits)}
    end)
    |> Enum.into(%{})
  end

  defp normalize_limit_bucket(limits) when is_map(limits) or is_list(limits) do
    limits =
      limits
      |> normalize_map()

    %{
      live_sessions: Map.get(limits, :live_sessions, @default_limits["tier_a"].live_sessions),
      concurrent_browser_contexts:
        Map.get(
          limits,
          :concurrent_browser_contexts,
          @default_limits["tier_a"].concurrent_browser_contexts
        ),
      concurrent_effectful_actions:
        Map.get(
          limits,
          :concurrent_effectful_actions,
          @default_limits["tier_a"].concurrent_effectful_actions
        )
    }
  end

  defp normalize_map(value) when is_map(value) do
    value
    |> Enum.map(fn {key, item} -> {normalize_key(key), item} end)
    |> Enum.into(%{})
  end

  defp normalize_map(value) when is_list(value), do: value |> Map.new() |> normalize_map()

  defp normalize_key(key) when is_atom(key), do: key

  defp normalize_key(key) when is_binary(key) do
    try do
      String.to_existing_atom(key)
    rescue
      ArgumentError -> key
    end
  end
end
