defmodule Aegis.Policy.ToolRegistry do
  @moduledoc """
  Phase 07 tool descriptor registry boundary.

  Source of truth:
  - phase doc: `docs/exec-plans/active/PHASE-07-policy-approvals.md`
  - ADRs: `docs/adr/0008-protobuf-jsonschema-contracts.md`,
    `docs/adr/0011-policy-approval-boundary.md`
  - acceptance: `AC-028`
  - tests: `TS-009` (`python3 scripts/run_policy_suite.py`)

  Descriptors are generated from `schema/tool-registry.yaml` and validated against
  `schema/jsonschema/tool-descriptor.schema.json`.
  """

  alias Aegis.Policy.Generated.ToolRegistry, as: GeneratedToolRegistry

  @spec all() :: [map()]
  def all, do: GeneratedToolRegistry.tools()

  @spec tool_ids() :: [String.t()]
  def tool_ids do
    GeneratedToolRegistry.by_tool_id()
    |> Map.keys()
    |> Enum.sort()
  end

  @spec fetch(String.t()) :: {:ok, map()} | {:error, :unknown_tool}
  def fetch(tool_id) when is_binary(tool_id) do
    case Map.get(GeneratedToolRegistry.by_tool_id(), tool_id) do
      nil -> {:error, :unknown_tool}
      descriptor -> {:ok, descriptor}
    end
  end

  @spec fetch!(String.t()) :: map()
  def fetch!(tool_id) when is_binary(tool_id) do
    case fetch(tool_id) do
      {:ok, descriptor} ->
        descriptor

      {:error, :unknown_tool} ->
        raise ArgumentError, "unknown tool descriptor #{inspect(tool_id)}"
    end
  end

  @spec by_executor(String.t()) :: [map()]
  def by_executor(executor_kind) when is_binary(executor_kind) do
    all()
    |> Enum.filter(&(Map.fetch!(&1, "executor_kind") == executor_kind))
  end

  @spec registry_version() :: pos_integer()
  def registry_version, do: GeneratedToolRegistry.registry_version()

  @spec source_digest() :: String.t()
  def source_digest, do: GeneratedToolRegistry.source_digest()

  @spec source_files() :: [String.t()]
  def source_files, do: GeneratedToolRegistry.source_files()
end
