defmodule Aegis.Policy.RbacRoles do
  @moduledoc """
  Generated RBAC role catalog boundary for Phase 09 authorization decisions.
  """

  alias Aegis.Policy.Generated.RbacRoles, as: GeneratedRoles

  @spec all() :: [map()]
  def all, do: GeneratedRoles.roles()

  @spec ids() :: [String.t()]
  def ids do
    GeneratedRoles.by_id()
    |> Map.keys()
    |> Enum.sort()
  end

  @spec fetch(String.t()) :: {:ok, map()} | {:error, :unknown_role}
  def fetch(role_id) when is_binary(role_id) do
    case Map.get(GeneratedRoles.by_id(), role_id) do
      nil -> {:error, :unknown_role}
      role -> {:ok, role}
    end
  end

  @spec fetch!(String.t()) :: map()
  def fetch!(role_id) when is_binary(role_id) do
    case fetch(role_id) do
      {:ok, role} -> role
      {:error, :unknown_role} -> raise ArgumentError, "unknown RBAC role #{inspect(role_id)}"
    end
  end

  @spec source_digest() :: String.t()
  def source_digest, do: GeneratedRoles.source_digest()
end
