# Must Not Violate

These constraints are hard stops. Do not violate them even under schedule pressure.

## INV-001 — Session is the primary runtime abstraction
Every long-lived unit of AI work is modeled as a session; requests, chats, jobs, and workflows are subordinate views.

Why it matters: The whole system is designed around durable, stateful, operator-visible sessions. Losing this abstraction makes Elixir incidental and destroys replay, recovery, and ownership semantics.

## INV-002 — Exactly one authoritative live owner exists per session
A session may have many observers and many execution workers, but only one BEAM owner may advance authoritative session state at a time.

Why it matters: This prevents split-brain, duplicate side effects, and impossible-to-debug races.

## INV-003 — Session timelines are append-only and event-sourced
Session history is never mutated in place. Events are appended with per-session sequence numbers and hash chaining.

Why it matters: Append-only timelines are the foundation for recovery, audit, replay, and operator trust.

## INV-004 — Side effects launch only from committed intent via an outbox
No external tool, worker, browser, or side-effecting action may start until intent has been durably committed and published through the outbox path.

Why it matters: This avoids ghost actions, lost dispatches, and dual-write inconsistency.

## INV-005 — Per-session total order is mandatory
Within a session, events must be totally ordered by authoritative sequence number; global total order is explicitly not required.

Why it matters: Per-session total order is sufficient for correctness and far cheaper than global serialization.

## INV-006 — Heavy model, browser, and media work must stay off BEAM schedulers
Elixir coordinates and supervises; Python and Rust execute heavy or low-level work.

Why it matters: The control plane must remain responsive and recoverable under load.

## INV-007 — Workers never own authoritative state
Python and Rust workers may hold transient execution context but may not mutate canonical runtime tables or become the source of truth.

Why it matters: Recovery must come from the control plane, not from hidden worker state.

## INV-008 — Humans and approvals are first-class runtime participants
Operator intervention, approvals, takeover, notes, and return-to-automation must be represented as timeline events and runtime state transitions.

Why it matters: Aegis is not credible if human control exists outside the runtime.

## INV-009 — Every effectful action crosses an explicit policy boundary
Tool execution must be classified and gated as allow, allow-with-constraints, require-approval, or deny before dispatch.

Why it matters: Policy is part of correctness and trust, not middleware.

## INV-010 — Every external side effect has an idempotency strategy
Each tool/action descriptor must declare idempotency class and compensation strategy or be marked uncertain on retry.

Why it matters: Exactly-once is not generally available; uncertainty must be explicit.

## INV-011 — Checkpoints are mandatory
Sessions must use structured checkpoints plus tail replay; genesis replay only is not acceptable.

Why it matters: Long sessions must hydrate quickly and safely after crashes or transfers.

## INV-012 — Replay must not require re-executing the world
Historical replay uses recorded events and artifacts; nondeterministic outputs are consumed from the timeline, not regenerated.

Why it matters: Operators need a reliable forensic record, not a best-effort reenactment.

## INV-013 — Owners self-fence on lease ambiguity
If a node cannot prove its lease, it must stop dispatching side effects and enter a fenced/degraded mode.

Why it matters: Correctness beats availability when ownership is ambiguous.

## INV-014 — Artifact blobs do not transit the control plane
Large screenshots, traces, and recordings move via signed object storage paths and are referenced by metadata in the control plane.

Why it matters: The control plane must carry intent and metadata, not hot binary payloads.

## INV-015 — Cross-language contracts are explicit and versioned
Runtime messages use Protobuf and tool I/O uses JSON Schema; version negotiation is required.

Why it matters: Without hard contracts, multi-language orchestration becomes distributed spaghetti.

## INV-016 — Tenant and workspace scoping are universal
Every durable object, event, artifact, and action includes tenant and workspace identity, and enforcement is not optional.

Why it matters: Enterprise trust and future deployment tiers depend on isolation being built in from day one.

## INV-017 — The runtime must be inspectable by design
Timelines, owner identity, in-flight actions, approvals, checkpoints, and recovery history must be visible at the session and operator level.

Why it matters: Complex AI systems are unusable without strong operator visibility.

## INV-018 — Sidecars over NIFs for hot paths
Media, protocol, recording, and performance-critical work that risks scheduler health must run in sidecars rather than nontrivial NIFs.

Why it matters: Isolation and crash containment matter more than embedding everything into Elixir.

## INV-019 — Browser writes are dangerous by default
Browser mutations start from a higher-risk classification than browser reads and usually require approval or tighter policy.

Why it matters: The first wedge deals with messy admin surfaces where unintended writes are costly.

## INV-020 — Direct worker writes to canonical tables are forbidden
Execution-plane components may not write to sessions, events, checkpoints, leases, approvals, or outbox tables.

Why it matters: Allowing worker-side authority breaks the ownership model and replay guarantees.
