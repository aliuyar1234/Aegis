defmodule Aegis.Runtime.OwnershipGuide do
  @moduledoc """
  Code-adjacent ownership guide and golden examples for the Phase 01 session tree.

  This module exists to keep the runtime model close to the code that implements it.
  It documents which process owns which category of state and provides a small golden
  example that new contributors can compare against the live `SessionKernel` flow.

  Golden flow:

      iex> example = Aegis.Runtime.OwnershipGuide.golden_example()
      iex> Enum.map(example.commands, &elem(&1, 0))
      [:activate, :request_action, :wait, :change_control_mode, :register_artifact]

  That example keeps authoritative state in `SessionKernel` while every child process
  stays strictly ephemeral.
  """

  @process_owners [
    %{
      process: Aegis.Runtime.SessionKernel,
      owns: [
        "phase, control_mode, health, wait_reason",
        "last committed seq_no",
        "action ledger, approvals, child agents, browser handles",
        "stable operator projection fields"
      ]
    },
    %{
      process: Aegis.Runtime.ParticipantBridge,
      owns: ["presence metadata", "socket references"]
    },
    %{
      process: Aegis.Runtime.TimerManager,
      owns: ["in-process timer references", "retry wakeup refs"]
    },
    %{
      process: Aegis.Runtime.CheckpointWorker,
      owns: ["checkpoint trigger bookkeeping"]
    },
    %{
      process: Aegis.Runtime.ToolRouter,
      owns: ["execution handles", "worker heartbeat references"]
    },
    %{
      process: Aegis.Runtime.PolicyCoordinator,
      owns: ["policy request correlation", "pending evaluation refs"]
    },
    %{
      process: Aegis.Runtime.ChildAgentSupervisor,
      owns: ["child agent process supervision only"]
    },
    %{
      process: Aegis.Runtime.EventFanout,
      owns: ["subscriber refs", "local delivery bookkeeping"]
    },
    %{
      process: Aegis.Runtime.ArtifactCoordinator,
      owns: ["artifact handoff refs", "upload confirmations"]
    }
  ]

  @golden_example %{
    session_attributes: %{
      session_id: "session-golden",
      tenant_id: "tenant-demo",
      workspace_id: "workspace-demo",
      requested_by: "golden-example",
      session_kind: "browser_operation"
    },
    commands: [
      {:activate, %{owner_node: "runtime@node", lease_epoch: 1}},
      {:request_action,
       %{
         action_id: "action-open-browser",
         tool_id: "browser.open",
         tool_schema_version: "v1",
         risk_class: "read_only",
         idempotency_class: "idempotent",
         timeout_class: "standard",
         mutating: false
       }},
      {:wait, :approval, %{detail: "awaiting operator approval"}},
      {:change_control_mode, :supervised, %{reason: "operator shadowing"}},
      {:register_artifact,
       %{
         artifact_id: "artifact-browser-screenshot",
         artifact_kind: "screenshot",
         storage_ref: "s3://aegis-artifacts/artifact-browser-screenshot"
       }}
    ],
    expected_projection: %{
      phase: "waiting",
      control_mode: "supervised",
      wait_reason: "approval",
      in_flight_action_ids: ["action-open-browser"],
      recent_artifact_ids: ["artifact-browser-screenshot"]
    }
  }

  @spec process_owners() :: [map()]
  def process_owners, do: @process_owners

  @spec golden_example() :: map()
  def golden_example, do: @golden_example
end
