# Product Definition

## Locked project definition

**Aegis Runtime** is a **BEAM-native durable runtime and control plane for long-lived AI sessions**.

A session is a live unit of work that may span:

- models and planners
- browser actions
- tool calls
- timers and retries
- policy gates and approvals
- operator intervention
- artifacts such as screenshots and traces
- future voice/media streams

Aegis owns the lifecycle, orchestration, durability, replay, governance, recovery, and operator visibility of those sessions.

## What Aegis is

- A runtime for stateful, failure-prone AI work
- A control plane for long-lived sessions
- A supervised orchestration backbone
- An operator-facing mission-control system
- A foundation for downstream products and domain packs

## What Aegis is not

- Not a generic chat app
- Not a model-serving platform
- Not a vector database
- Not a telephony carrier
- Not a browser cloud as the primary product
- Not a low-code workflow builder
- Not a thin wrapper around frontier model APIs
- Not a generic “AI agent builder” demo product

## Category

**AI runtime / agent control plane / durable session orchestration platform**

## Problem Aegis solves

Most “agent” stacks are still fragile combinations of SDK calls, async workers, queue semantics, browser processes, and dashboards. They can demo well and still fail badly in production. The common failure modes are predictable:

- partial failure and orphaned work
- duplicate side effects
- lost ownership after crashes or partitions
- no usable replay model
- no clear policy or approval boundary
- no reliable human takeover path
- no stable cross-language contract
- no operator confidence under load

Aegis exists to solve the **runtime layer** of that problem.

## Target users

Primary users:

- AI platform teams
- infrastructure/platform engineering teams
- product teams building high-value service automation
- operators who need to inspect, approve, and recover live sessions

Secondary users later:

- enterprises standardizing on durable AI operations
- OSS adopters extending the runtime core
- cloud customers using a managed control plane

## Why this must exist

The AI ecosystem is converging on long-lived, tool-using, multimodal systems that act across browsers, tools, and enterprise software. The market has model APIs, browser automation tools, and observability fragments. It is still missing a truly strong, BEAM-native runtime that treats these interactions as supervised sessions with durable recovery and human control.

Aegis is the layer that makes ambitious agent systems operationally credible.

## Why Elixir is mission-critical

Elixir is not here by accident. Aegis uses Elixir because the central problem is not “calling an LLM.” The central problem is:

- coordinating massive numbers of concurrent live sessions
- isolating failure cleanly
- supervising long-lived process trees
- managing timers, retries, and stateful wait conditions
- streaming updates to operators in real time
- preserving responsiveness under partial failure
- recovering sessions after process or node loss
- enforcing backpressure and admission control

Those are BEAM-native strengths.

## Why Python is necessary

Python is required for the execution plane because that is where the ecosystem gravity still lives:

- model and provider SDKs
- browser automation stacks
- eval tooling
- many tool adapters
- flexible prompt assembly and structured output handling

Python executes work. It does not become the source of truth.

## Why Rust is necessary

Rust is required for the hot paths and the hard boundaries:

- media/protocol bridges
- recording and compression sidecars
- performance-critical adapters
- future voice/media expansion
- any path where scheduler safety and binary throughput matter

Rust is about isolation and performance, not control-plane ownership.

## First wedge

The locked first wedge is **browser-backed service operations**:

- browser-driven account remediation
- billing/support flows in messy admin surfaces
- internal SaaS workflows that combine reads, writes, and approvals
- operations work that often needs human takeover

This wedge forces Aegis to solve the right hard problems early.

## Runtime core vs downstream products

**Runtime core owns:**

- session lifecycle and ownership
- event timeline, checkpoints, and replay
- policy and approval boundaries
- action dispatch and recovery
- operator console and intervention
- contracts and artifacts
- quotas, tenant context, and auditability

**Downstream products own:**

- business-specific workflows
- domain-specific prompts, tools, and integrations
- customer-facing UI
- product packaging for vertical use cases

Aegis is the substrate, not every product built on top of it.

## Long-term platform shape

Long term, Aegis can support:

- browser operations
- voice/media sessions
- domain packs
- connector SDKs
- managed-cloud control plane offerings
- OSS core with enterprise and managed layers above it

The core thesis does not change: **the session runtime is the product center of gravity**.
