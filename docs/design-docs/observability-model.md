# Observability model

Aegis must be inspectable by design.

## Three layers of observability

### 1) Events
Authoritative runtime truth.  
Use events to answer: **what happened?**

### 2) Traces
Causal execution chain across control and execution planes.  
Use traces to answer: **where did time and failure flow?**

### 3) Logs
Diagnostic detail for developers.  
Use logs to answer: **what was the code doing?**

Events are not optional. Logs are not a substitute for events.

## Tracing

Create a root trace per session and propagate trace context through:
- API admission
- SessionKernel command handling
- event append
- outbox publish
- JetStream dispatch
- worker execution
- artifact registration
- replay or recovery paths

Store `trace_id` in event envelopes so timeline and tracing can be correlated.

## Metrics

Track at least:

### Session metrics
- lifecycle duration
- wait time by reason
- action retry counts
- recovery count
- approval wait duration
- uncertain-side-effect count

### Node metrics
- owned sessions
- lease renew latency
- mailbox pressure
- append latency
- recovery throughput

### System metrics
- Postgres latency and errors
- JetStream lag
- artifact-store failures
- worker saturation
- adoption count
- projection freshness

## Operator console requirements

A live session page must show:
- current owner
- lifecycle state
- last committed seq_no
- latest checkpoint
- in-flight actions and deadlines
- pending approvals
- artifacts
- latest failures
- intervention controls

A replay page must show:
- timeline scrubber
- artifact playback
- approval and operator overlays
- checkpoint markers
- action lineage

## Debugging workflow

The expected debugging path is:

1. Open session timeline.
2. Identify last committed action and owner.
3. Inspect approval and policy history.
4. Inspect artifact evidence.
5. Jump to correlated trace if deeper execution detail is needed.
6. Use runbook if failure class is operational.

If debugging requires tailing raw logs first, Aegis is failing its observability goal.
