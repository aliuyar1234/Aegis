# Runtime model

This is the canonical design for the Aegis runtime.

## Canonical abstraction: Session

A session is the authoritative unit of AI work. It has:

- identity (`session_id`, `tenant_id`, `workspace_id`)
- lifecycle (`phase`, `control_mode`, `health`)
- one authoritative live owner
- an append-only timeline
- structured checkpoints
- in-flight action ledger
- pending approvals
- timers and deadlines
- artifacts
- participants (agents and humans)

Everything else is subordinate.

## Lifecycle model

A session uses orthogonal state fields rather than one giant enum.

### Phase
- `provisioning`
- `hydrating`
- `active`
- `waiting`
- `cancelling`
- `terminal`

### Control mode
- `autonomous`
- `supervised`
- `human_control`
- `paused`

### Health
- `healthy`
- `degraded`
- `quarantined`

### Wait reason
- `action`
- `approval`
- `timer`
- `external_dependency`
- `operator`
- `lease_recovery`

## Supervisor hierarchy

```text
Aegis.Runtime.SessionHostSupervisor (DynamicSupervisor)
└── Aegis.Runtime.SessionTreeSupervisor (:rest_for_one)
    ├── SessionKernel
    ├── ParticipantBridge
    ├── TimerManager
    ├── CheckpointWorker
    ├── ToolRouter
    ├── PolicyCoordinator
    ├── ChildAgentSupervisor
    ├── EventFanout
    └── ArtifactCoordinator
```

### Why `:rest_for_one`
`SessionKernel` is the authoritative state owner. If it crashes, dependent processes must rebuild around restored state. If a dependent process crashes, the kernel may survive.

## Process ownership

### SessionKernel owns authoritative in-memory state
- phase, mode, health
- last committed `seq_no`
- action ledger
- pending approvals
- durable variables and summaries
- child agent descriptors
- timer metadata
- participant roles
- external handles
- artifact references
- lease epoch

### Other processes own only ephemeral state
- `ToolRouter` — execution handles, heartbeat refs
- `TimerManager` — live timer refs
- `ParticipantBridge` — Presence and socket refs
- `ArtifactCoordinator` — signed URL handoffs and upload confirmations
- child agents — transient planning state only

## Child agent model

Child agents are logical actors inside a session. They may have their own processes, but they do not own session truth and do not append events directly.

Each child agent has:

- `agent_id`
- `role`
- `goal`
- `budget`
- `tool_allowlist`
- `output_contract`
- `state_summary`

Child-agent work enters the session through intents.

## Action model

Actions are the only path to external work. Each action has:

- `action_id`
- `tool_id`
- `risk_class`
- `idempotency_class`
- `timeout_class`
- `retry_policy`
- `input_ref`
- `approval_requirement`
- `execution_status`
- zero or more `execution_id` attempts

By default, only one **effectful** action may be in flight per session. Safe read-only work can later be parallelized selectively.

## Policy and approval model

Every action request enters `Aegis.Policy` before dispatch.

Decision classes:
- `allow`
- `allow_with_constraints`
- `require_approval`
- `deny`

Approvals are bound to:
- `action_hash`
- `lease_epoch`
- approver identity
- expiry time

## Timer and retry model

Two timer classes:

- **short timers** — in-process timers with durable deadline recorded in state
- **durable timers** — scheduled jobs for longer waits and retries

Retry is driven by action metadata, not hidden worker logic.

## Checkpoints

Checkpoints are structured projections of session state. They are created:

- after session creation
- after terminal action outcomes
- before long waiting states
- before/after human control
- after adoption or recovery
- at bounded event-count thresholds

Checkpoint content:
- projection version
- session lifecycle fields
- action ledger
- pending approvals
- deadlines
- external handle refs
- summary memory
- artifact refs
- last committed seq_no

## Human handoff model

Human intervention is a runtime state transition, not an out-of-band hack.

Flow:
1. `handoff_requested` or approval block occurs
2. session enters `waiting/operator` or `human_control`
3. autonomous dispatch pauses
4. operator joins
5. operator inspects, annotates, retries, approves, or takes over browser path
6. operator returns control with context

All of those steps are timeline events.

## Durable vs ephemeral state

### Durable
- session timeline
- structured session projection
- checkpoints
- approvals
- action ledger
- external handles
- artifact metadata
- operator notes

### Ephemeral
- process refs
- sockets
- worker heartbeats
- browser websocket attachments
- prompt assembly caches
- local projections

## Reconstruction boundaries

Can reconstruct from event log + checkpoints:
- lifecycle state
- action history
- approvals
- participants
- summaries
- artifact refs
- ownership transfers

Cannot reconstruct purely from the log:
- live browser process memory
- open sockets
- worker-local scratch state
- external world state unless recorded

That boundary is deliberate.
