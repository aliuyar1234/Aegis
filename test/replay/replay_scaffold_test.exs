defmodule ReplayScaffoldTest do
  use ExUnit.Case, async: true

  test "checkpoint, event catalog, replay fixture, and migration files exist" do
    assert File.exists?("schema/checkpoints/session-checkpoint-v1.schema.json")
    assert File.exists?("schema/event-catalog/events.yaml")
    assert File.exists?("schema/event-catalog/index.yaml")
    assert File.exists?("test/replay/fixtures/golden_timeline_example.exs")

    assert File.exists?(
             "apps/aegis_events/priv/postgres/migrations/202603080001_phase_02_core.sql"
           )
  end
end
