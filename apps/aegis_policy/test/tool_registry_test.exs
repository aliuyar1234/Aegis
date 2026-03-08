defmodule Aegis.Policy.ToolRegistryTest do
  use ExUnit.Case, async: true

  alias Aegis.Policy.ToolRegistry

  test "lists descriptors and fetches a known browser tool" do
    assert ToolRegistry.registry_version() == 1
    assert ToolRegistry.tool_ids() == [
             "browser.click",
             "browser.delete",
             "browser.navigate",
             "browser.open",
             "browser.submit"
           ]
    assert is_binary(ToolRegistry.source_digest())
    assert String.length(ToolRegistry.source_digest()) == 64

    assert {:ok, descriptor} = ToolRegistry.fetch("browser.navigate")
    assert descriptor["executor_kind"] == "python"
    assert descriptor["risk_class"] == "browser_read"
    assert descriptor["timeout_class"] == "medium"
    assert descriptor["required_scopes"] == ["browser.navigate", "artifact.capture"]
  end

  test "filters by executor kind and rejects unknown tools" do
    descriptors = ToolRegistry.by_executor("python")

    assert Enum.map(descriptors, &Map.fetch!(&1, "tool_id")) == [
             "browser.click",
             "browser.delete",
             "browser.navigate",
             "browser.open",
             "browser.submit"
           ]

    assert {:error, :unknown_tool} = ToolRegistry.fetch("browser.unknown")

    assert_raise ArgumentError, ~r/unknown tool descriptor/, fn ->
      ToolRegistry.fetch!("browser.unknown")
    end
  end
end
