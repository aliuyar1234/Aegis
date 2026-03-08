defmodule Aegis.Events.Catalog do
  @moduledoc false

  @events %{
    "session.created" => %{version: 1, determinism_class: "deterministic"},
    "session.hydrated" => %{version: 1, determinism_class: "deterministic"},
    "session.owned" => %{version: 1, determinism_class: "deterministic"},
    "session.mode_changed" => %{version: 1, determinism_class: "deterministic"},
    "session.waiting" => %{version: 1, determinism_class: "deterministic"},
    "session.resumed" => %{version: 1, determinism_class: "deterministic"},
    "session.cancelling" => %{version: 1, determinism_class: "deterministic"},
    "session.completed" => %{version: 1, determinism_class: "deterministic"},
    "session.failed" => %{version: 1, determinism_class: "deterministic"},
    "session.quarantined" => %{version: 1, determinism_class: "deterministic"},
    "system.lease_lost" => %{version: 1, determinism_class: "deterministic"},
    "system.node_recovered" => %{version: 1, determinism_class: "deterministic"},
    "health.degraded" => %{version: 1, determinism_class: "deterministic"},
    "agent.spawned" => %{version: 1, determinism_class: "deterministic"},
    "action.requested" => %{version: 1, determinism_class: "deterministic"},
    "action.dispatched" => %{version: 1, determinism_class: "deterministic"},
    "action.progressed" => %{version: 1, determinism_class: "nondeterministic_external"},
    "action.heartbeat_missed" => %{version: 1, determinism_class: "deterministic"},
    "action.succeeded" => %{version: 1, determinism_class: "nondeterministic_external"},
    "action.failed" => %{version: 1, determinism_class: "nondeterministic_external"},
    "action.cancel_requested" => %{version: 1, determinism_class: "deterministic"},
    "action.cancelled" => %{version: 1, determinism_class: "nondeterministic_external"},
    "approval.requested" => %{version: 1, determinism_class: "deterministic"},
    "artifact.registered" => %{version: 1, determinism_class: "deterministic"},
    "system.worker_lost" => %{version: 1, determinism_class: "deterministic"},
    "checkpoint.created" => %{version: 1, determinism_class: "deterministic"},
    "checkpoint.restored" => %{version: 1, determinism_class: "deterministic"}
  }

  def fetch!(type), do: Map.fetch!(@events, type)
  def known?(type), do: Map.has_key?(@events, type)
end
