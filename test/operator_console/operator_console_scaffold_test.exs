defmodule OperatorConsoleScaffoldTest do
  use ExUnit.Case, async: true

  test "operator session view schema exists" do
    assert File.exists?("schema/jsonschema/operator-session-view.schema.json")
    assert File.exists?("docs/product-specs/operator-console.md")
  end
end
