defmodule Aegis.Projection.RunbookLinks do
  @moduledoc """
  Runbook-link helper for Phase 06 operator surfaces.

  This module mirrors the machine-readable mappings in:
  - `meta/operator-surfaces.yaml`
  - `meta/failure-runbooks.yaml`

  Keep these lists aligned with those files as operator surfaces evolve.
  """

  @surface_runbooks %{
    "session-fleet" => [
      "docs/runbooks/degraded-system-mode.md",
      "docs/runbooks/transport-lag.md"
    ],
    "session-detail" => [
      "docs/runbooks/worker-crash.md",
      "docs/runbooks/node-loss.md",
      "docs/runbooks/lease-ambiguity.md",
      "docs/runbooks/browser-instability.md",
      "docs/runbooks/artifact-store-outage.md",
      "docs/runbooks/operator-intervention.md"
    ],
    "approvals-queue" => [
      "docs/runbooks/approval-timeout.md"
    ],
    "replay" => [
      "docs/runbooks/event-corruption-quarantine.md",
      "docs/runbooks/duplicate-execution.md"
    ]
  }

  @failure_runbooks [
    %{
      surface: "session-detail",
      events: ["system.worker_lost", "action.heartbeat_missed"],
      runbook: "docs/runbooks/worker-crash.md"
    },
    %{
      surface: "session-detail",
      events: ["system.lease_lost", "system.node_recovered"],
      runbook: "docs/runbooks/node-loss.md"
    },
    %{
      surface: "session-detail",
      events: ["system.lease_lost", "health.degraded"],
      runbook: "docs/runbooks/lease-ambiguity.md"
    },
    %{
      surface: "session-detail",
      events: ["observation.browser_snapshot_added", "action.failed"],
      runbook: "docs/runbooks/browser-instability.md"
    },
    %{
      surface: "session-detail",
      events: ["artifact.registered"],
      runbook: "docs/runbooks/artifact-store-outage.md"
    },
    %{
      surface: "session-detail",
      events: [
        "operator.joined",
        "operator.paused",
        "operator.took_control",
        "operator.returned_control",
        "operator.abort_requested"
      ],
      runbook: "docs/runbooks/operator-intervention.md"
    },
    %{
      surface: "replay",
      events: ["action.succeeded", "action.failed"],
      runbook: "docs/runbooks/duplicate-execution.md"
    },
    %{
      surface: "replay",
      events: ["checkpoint.restored"],
      runbook: "docs/runbooks/event-corruption-quarantine.md"
    }
  ]

  @spec for_surface(String.t()) :: [map()]
  def for_surface(surface_id) when is_binary(surface_id) do
    @surface_runbooks
    |> Map.get(surface_id, [])
    |> Enum.map(&entry/1)
  end

  @spec for_timeline(String.t(), [map()], keyword()) :: [map()]
  def for_timeline(surface_id, timeline, opts \\ []) when is_binary(surface_id) do
    event_types = MapSet.new(Enum.map(timeline, & &1.type))

    matched =
      @failure_runbooks
      |> Enum.filter(&(&1.surface == surface_id))
      |> Enum.filter(fn rule ->
        Enum.any?(rule.events, &MapSet.member?(event_types, &1))
      end)
      |> Enum.map(& &1.runbook)

    extras =
      if Keyword.get(opts, :approval_wait, false) do
        ["docs/runbooks/approval-timeout.md"]
      else
        []
      end

    (@surface_runbooks[surface_id] || [])
    |> Kernel.++(matched)
    |> Kernel.++(extras)
    |> Enum.uniq()
    |> Enum.map(&entry/1)
  end

  defp entry(path) do
    %{
      path: path,
      label:
        path
        |> Path.basename(".md")
        |> String.replace("-", " ")
    }
  end
end
