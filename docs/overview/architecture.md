# Architecture Overview

## Top-level architecture

```text
                         ┌──────────────────────────────┐
                         │   Operator / Product UIs     │
                         │ LiveView console + APIs      │
                         └──────────────┬───────────────┘
                                        │
                           HTTPS / WS / SSE / gRPC
                                        │
                     ┌───────────────────▼───────────────────┐
                     │         Elixir Control Plane          │
                     │                                       │
                     │  Gateway / Auth / Tenancy            │
                     │  Session Runtime / Lease Manager     │
                     │  Policy & Approvals                  │
                     │  Event Store / Replay / Checkpoints  │
                     │  Outbox / Projections / PubSub       │
                     └──────────────┬───────────────┬───────┘
                                    │               │
                          Postgres tx│               │PubSub/Channels
                                    │               │
                    ┌───────────────▼───────┐   ┌───▼─────────────────┐
                    │   PostgreSQL          │   │ Live read models     │
                    │ sessions/events/      │   │ session views        │
                    │ leases/outbox/checkpt │   │ approval queues      │
                    └───────────────┬───────┘   └──────────────────────┘
                                    │
                         outbox publish / replay
                                    │
                         ┌──────────▼──────────┐
                         │  NATS JetStream     │
                         │ command + progress  │
                         │ + durable streams   │
                         └───────┬───────┬─────┘
                                 │       │
                     ┌───────────▼─┐   ┌─▼─────────────────┐
                     │ Python exec │   │ Rust sidecars     │
                     │ planner     │   │ recorder/media    │
                     │ browser     │   │ protocol bridges  │
                     │ tools       │   └──────────┬────────┘
                     └──────┬──────┘              │
                            │                     │
                    ┌───────▼─────────────────────▼────────┐
                    │          Data / Execution Plane      │
                    │ browser contexts, model APIs, tools, │
                    │ future voice/media rooms             │
                    └───────┬──────────────────────────────┘
                            │
                    ┌───────▼──────────────────────────────┐
                    │  S3-compatible Artifact Store        │
                    │ screenshots / traces / DOM / blobs   │
                    └──────────────────────────────────────┘
```

## System thesis

Aegis is built around one idea: **an agentic unit of work is closer to a supervised telecom session than to a stateless web request**.  
That means the architecture is organized around durable session ownership, append-only timelines, operator visibility, and safe recovery.

## Control plane vs execution plane vs data plane

### Control plane (Elixir)
Owns truth and coordination:

- session lifecycle
- lease ownership
- event append and replay
- checkpoints
- policy and approvals
- outbox and dispatch intent
- operator console and PubSub
- quotas, tenancy, audit, observability

### Execution plane (Python / Rust)
Executes external work:

- browser automation
- planner/model-heavy actions
- tool adapters
- future media/voice sidecars
- recorders and protocol bridges

Execution plane components are replaceable. They are **not** authoritative.

### Data plane
The external environments Aegis acts against:

- browsers and SaaS surfaces
- model providers
- tool endpoints
- future telephony and media systems
- object storage for artifacts

## Major subsystems

| Subsystem | Responsibility |
|---|---|
| `aegis_gateway` | APIs, auth, tenancy resolution, LiveView/Channels, operator entry point |
| `aegis_runtime` | SessionKernel, supervisor trees, command handling, runtime lifecycle |
| `aegis_leases` | Lease creation, renewal, fencing, and adoption |
| `aegis_events` | Event append, replay, upcasting, integrity checks |
| `aegis_policy` | Tool registry, risk classification, approvals, capability token issuance |
| `aegis_execution_bridge` | Outbox consumers, JetStream dispatch, worker heartbeats, cancellations |
| `aegis_artifacts` | Artifact metadata, signed URLs, retention and redaction hooks |
| `aegis_projection` | Read models and views for operator surfaces |
| `aegis_obs` | Tracing, metrics, quality instrumentation, health projections |
| Python workers | Browser, planner, tool, and later eval/speech execution |
| Rust sidecars | Recorder, protocol bridges, future media gateway |

## Service boundaries

### Elixir boundaries
The Elixir control plane is a set of bounded umbrella applications. Keep boundaries explicit:

- runtime code does not reach into browser implementation details
- policy code does not own persistence logic beyond its own decisions
- projections are read-optimized views, not authoritative state
- gateway/UI code does not bypass runtime APIs

### Python boundaries
Python services may:

- execute browser/model/tool work
- upload artifacts
- emit progress and completion
- consume capability tokens and scope-limited inputs

Python services may **not**:

- assign authoritative seq_no
- mutate canonical session state
- self-approve dangerous actions
- write control-plane tables directly

### Rust boundaries
Rust sidecars may:

- handle binary-heavy and latency-critical work
- transform, compress, or record streams
- expose gRPC or message-based interfaces to the control plane

Rust sidecars may **not**:

- own session state
- bypass policy or approval models
- become a hidden orchestration layer

## Sync vs async boundaries

### Synchronous
Keep these synchronous and transactional:

- session admission
- command validation by the owner
- event append + outbox insert
- approval decisions
- lease claim/renew/release

### Asynchronous
Keep these async and failure-tolerant:

- external action dispatch
- progress callbacks
- artifact uploads
- projection updates
- long timers
- retry wakeups
- analytics exports

## Cluster topology

Initial topology is single-region, multi-pool:

- **Gateway pool** — Phoenix endpoints and LiveView
- **Runtime pool** — SessionKernel owners, leases, replay, policy
- **Projection pool** — optional early; can be colocated initially
- **Python pools** — planner, browser, tool, later eval/speech
- **Rust pools** — recorder, future media/protocol sidecars

Backplane services:

- PostgreSQL HA
- NATS JetStream cluster
- S3-compatible object storage
- Jaeger / OTEL collector for traces in dev

## Multitenancy model

Aegis uses three isolation tiers from the start:

- **Tier A shared plane** — shared control and execution plane with quotas
- **Tier B isolated execution** — shared control plane, dedicated execution pools
- **Tier C dedicated deployment** — dedicated control plane, execution plane, and secrets boundary

Every durable object carries `tenant_id` and usually `workspace_id`.

## Artifact model

Artifacts are immutable blobs:

- screenshot
- DOM snapshot
- browser trace
- recording segment
- raw model output blob
- tool I/O blob
- operator note attachment

The control plane stores **metadata and references only**. Blobs move via signed URLs to object storage.

## Storage model at a glance

- Postgres is the source of truth
- session events are append-only
- checkpoints are structured and versioned
- outbox drives cross-language dispatch
- artifacts are stored in S3-compatible storage
- analytics is explicitly off the operational path

## Transport model at a glance

- Postgres event log is truth
- NATS JetStream is transport
- Phoenix Channels/PubSub serve UI updates
- gRPC is reserved for streaming/hot-path sidecars where needed
- object storage handles large binary payloads

## Browser wedge implication

Because browser ops is the first wedge, the architecture must treat browser sessions as **resumable external execution contexts**. The control plane owns:

- browser handle metadata
- action intent and status
- artifacts and timeline
- operator takeover state
- uncertainty classification

It does **not** own the live browser process memory.

## Future voice/media expansion

Voice and media fit later as additional execution/data-plane packs. They do not change:

- session primacy
- single-owner semantics
- outbox-before-side-effects
- event + checkpoint + replay model
- operator and approval primacy

See `docs/design-docs/future-voice-media.md` for the expansion path.
