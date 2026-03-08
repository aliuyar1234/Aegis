defmodule ExecutionBridgeScaffoldTest do
  use ExUnit.Case, async: true

  test "transport topology and contracts exist" do
    assert File.exists?("schema/transport-topology.yaml")
    assert File.exists?("schema/proto/aegis/runtime/v1/worker.proto")
  end
end
