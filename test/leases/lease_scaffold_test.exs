defmodule LeaseScaffoldTest do
  use ExUnit.Case, async: true

  test "lease runbooks exist" do
    assert File.exists?("docs/runbooks/node-loss.md")
    assert File.exists?("docs/runbooks/lease-ambiguity.md")
  end

  test "phase 03 implementation assets exist" do
    assert File.exists?("apps/aegis_leases/priv/postgres/migrations/202603080002_phase_03_leases.sql")
    assert File.exists?("apps/aegis_runtime/test/leases/lease_recovery_test.exs")
  end
end
