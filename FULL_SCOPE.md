# FULL_SCOPE.md

Aegis is intentionally broader than an MVP. This document defines the **full platform shape** so early implementation choices do not dead-end the architecture.

## Scope layers

### Layer 1 — Runtime core
This is the non-negotiable foundation:

- session kernel
- single-owner lease model
- append-only event timelines
- checkpoints and replay
- policy and approvals
- action dispatch bridge
- operator console
- artifacts and auditability
- worker contracts

### Layer 2 — First product wedge
Browser-backed service operations:

- browser workers
- screenshots, traces, DOM artifacts
- operator takeover
- uncertain side-effect handling
- policy defaults for browser writes
- example service workflows

### Layer 3 — Platformization
Once the runtime is proven:

- connector SDK
- extension points for tools and packs
- MCP adapter boundary
- richer operator automation flows
- more mature quotas and tenancy controls
- managed execution pools

### Layer 4 — Strategic expansion
After the runtime and wedge are real:

- voice/media pack
- domain packs
- simulation/evaluation pack
- OSS core and managed cloud split
- enterprise dedicated deployments

## What belongs in the runtime core forever

These are permanent platform concerns:

- session lifecycle
- ownership and recovery
- event and checkpoint integrity
- policy and approval boundaries
- operator visibility and intervention
- contracts and versioning
- tenant scoping
- audit and redaction hooks

## What belongs outside the runtime core

These are product or extension concerns:

- vertical-specific workflow logic
- domain-specific tool packs
- customer-facing workflow UIs
- advanced sales/demo packaging
- custom model orchestration logic per vertical
- analytics/BI views

## Full-scope capabilities by maturity

### v1 runtime scope
- browser wedge
- session recovery
- approvals and operator control
- replay and artifacts
- quotas and tenant context
- internal and public demo quality

### v2 platform scope
- connectors and extension SDK
- richer tenant isolation options
- robust policy engine
- branch replay / controlled counterfactuals
- managed-cloud control plane primitives

### v3 strategic scope
- voice/media
- enterprise hardening
- release packaging split
- broader ecosystem and cloud packaging
- benchmark-grade reliability story

## What must never happen

Do not let “full scope” turn into “build everything at once.”  
The full-scope view exists to keep early work architecturally aligned, not to justify uncontrolled breadth.

## Core product line possibilities

Aegis can later support multiple product expressions without changing the runtime thesis:

- OSS runtime core
- managed control plane
- browser-ops packaged offering
- enterprise dedicated deployment
- future voice/media pack

But the runtime remains the center of gravity in all of them.
