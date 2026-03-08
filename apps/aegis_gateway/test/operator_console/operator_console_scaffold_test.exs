defmodule OperatorConsoleScaffoldTest do
  use ExUnit.Case, async: true

  test "operator session view schema exists" do
    assert File.exists?(Path.expand("../../../../schema/jsonschema/operator-session-view.schema.json", __DIR__))
    assert File.exists?(Path.expand("../../../../docs/product-specs/operator-console.md", __DIR__))
  end
end
