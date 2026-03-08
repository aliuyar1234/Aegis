defmodule Aegis.Policy.DangerousActionCatalog do
  @moduledoc """
  Generated dangerous-action catalog boundary for Phase 07 policy evaluation.
  """

  alias Aegis.Policy.Generated.DangerousActionCatalog, as: GeneratedCatalog

  @spec all() :: [map()]
  def all, do: GeneratedCatalog.dangerous_action_classes()

  @spec ids() :: [String.t()]
  def ids do
    GeneratedCatalog.by_id()
    |> Map.keys()
    |> Enum.sort()
  end

  @spec fetch(String.t()) :: {:ok, map()} | {:error, :unknown_dangerous_action_class}
  def fetch(class_id) when is_binary(class_id) do
    case Map.get(GeneratedCatalog.by_id(), class_id) do
      nil -> {:error, :unknown_dangerous_action_class}
      entry -> {:ok, entry}
    end
  end

  @spec fetch!(String.t()) :: map()
  def fetch!(class_id) when is_binary(class_id) do
    case fetch(class_id) do
      {:ok, entry} -> entry
      {:error, :unknown_dangerous_action_class} -> raise ArgumentError, "unknown dangerous action class #{inspect(class_id)}"
    end
  end

  @spec default_decision(String.t() | nil) :: String.t() | nil
  def default_decision(nil), do: nil

  @spec default_decision(String.t()) :: String.t()
  def default_decision(class_id) when is_binary(class_id) do
    fetch!(class_id)
    |> Map.fetch!("default_decision")
  end

  @spec source_digest() :: String.t()
  def source_digest, do: GeneratedCatalog.source_digest()
end
