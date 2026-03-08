%{
  session_state: %{
    session_id: "session-replay",
    tenant_id: "tenant-replay",
    workspace_id: "workspace-replay",
    isolation_tier: "tier_a",
    session_kind: "browser_operation",
    requested_by: "fixture",
    owner_node: "runtime@node",
    phase: "active",
    control_mode: "autonomous",
    health: "healthy",
    wait_reason: "none",
    lease_epoch: 1,
    last_seq_no: 2,
    deadlines: [],
    pending_approvals: [],
    action_ledger: [],
    child_agents: [],
    browser_handles: [],
    summary_capsule: %{
      planner_summary: "opened a browser session",
      salient_facts: ["customer record located"],
      operator_notes: []
    },
    artifact_ids: [],
    recent_artifacts: [],
    latest_recovery_reason: nil
  },
  raw_events: [
    %{
      seq_no: 1,
      type: "session.created",
      payload: %{
        isolation_tier: "tier_a",
        session_kind: "browser_operation",
        requested_by: "fixture"
      },
      recorded_at: ~U[2026-03-08 10:00:00Z]
    },
    %{
      seq_no: 2,
      type: "session.owned",
      payload: %{
        owner_node: "runtime@node",
        lease_epoch: 1,
        adoption_reason: "fixture-activation"
      },
      recorded_at: ~U[2026-03-08 10:00:30Z]
    }
  ],
  expected_types: [
    "session.created",
    "session.owned",
    "checkpoint.created"
  ]
}
