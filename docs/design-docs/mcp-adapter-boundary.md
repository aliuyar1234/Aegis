# MCP adapter boundary

This document defines how Aegis can integrate with MCP without turning MCP into the runtime's internal protocol.

## Core rule

MCP is an external adapter boundary.

It is not:

- the canonical control-plane protocol
- the session timeline format
- the worker event protocol
- the lease or ownership model
- the approval or policy decision format

The internal runtime protocol remains the Phase 01 through Phase 09 control-plane contract: Postgres truth, append-only session events, outbox-driven dispatch, and Protobuf worker envelopes.

## What an MCP adapter is

An MCP adapter is an extension that:

- connects to an external MCP server over `stdio`, `sse`, or `streamable_http`
- publishes one or more Aegis tool ids backed by that external MCP server
- translates session-owned action requests into MCP tool invocations
- translates MCP responses back into normal worker outputs and artifact references

## What an MCP adapter may do

- expose external MCP tools as normal Aegis tool descriptors
- run behind normal session ownership, dispatch, policy, approval, quota, and artifact rules
- capture MCP transcripts or derived artifacts as evidence
- apply tenant/workspace scoping through the surrounding Aegis action envelope

## What an MCP adapter may not do

- write canonical runtime tables directly
- append runtime events directly
- bypass outbox and dispatch ordering
- bypass policy, dangerous-action classification, approvals, or capability tokens
- replace `ActionDispatch`, `ActionAccepted`, `ActionProgress`, `ActionCompleted`, `ActionFailed`, or `ActionCancelled`
- redefine replay truth around raw MCP messages

## Contract shape

The machine-readable boundary lives in `schema/jsonschema/connector-manifest.schema.json` under the `mcp_adapter` interface.

Required boundary claims:

- `protocol_role` must be `external_tool_adapter`
- `session_binding.requires_session_owner_dispatch` must be `true`
- `session_binding.maps_to_action_requests_only` must be `true`
- `session_binding.returns_worker_events_only` must be `true`
- all `protocol_boundary` escape hatches are fixed to `false`

This keeps MCP adapters subordinate to the existing runtime instead of becoming a parallel orchestration layer.

## Tool translation

MCP adapters publish Aegis-facing tool ids.

Those tool ids remain subject to:

- tool-registry descriptor rules
- risk and dangerous-action classification
- tenant-tier allowlists
- policy evaluation
- approval and capability-token checks where applicable

The adapter is translation glue, not authority.

## Sample fixture

`tests/extensibility/fixtures/sample-mcp-adapter.yaml` demonstrates the bounded adapter shape used by `TS-014`.
