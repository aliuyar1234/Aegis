defmodule Aegis.Policy.AbacAttributes do
  @moduledoc """
  Generated ABAC attribute catalog boundary for Phase 09 authorization decisions.
  """

  alias Aegis.Policy.Generated.AbacAttributes, as: GeneratedAttributes

  @spec all() :: [map()]
  def all, do: GeneratedAttributes.attributes()

  @spec ids() :: [String.t()]
  def ids do
    GeneratedAttributes.by_id()
    |> Map.keys()
    |> Enum.sort()
  end

  @spec fetch(String.t()) :: {:ok, map()} | {:error, :unknown_attribute}
  def fetch(attribute_id) when is_binary(attribute_id) do
    case Map.get(GeneratedAttributes.by_id(), attribute_id) do
      nil -> {:error, :unknown_attribute}
      attribute -> {:ok, attribute}
    end
  end

  @spec source_digest() :: String.t()
  def source_digest, do: GeneratedAttributes.source_digest()
end
