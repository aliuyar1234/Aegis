# Extensibility surface

This document defines the bounded extension contract introduced in PHASE-10.

## Goal

Allow third-party connectors and artifact processors to extend Aegis without bypassing runtime ownership, policy, replay, or audit guarantees.

## Boundary

- extensions are declarative manifests plus SDK entrypoints
- extensions never become the canonical runtime protocol
- extensions do not write control-plane truth directly
- extensions execute behind the same policy, approval, artifact, and tenancy boundaries as built-in workers

## Common manifest contract

Every extension manifest declares:

- stable identity: `id`, `display_name`, `version`, `kind`
- SDK boundary: implementation language, package, and entry module
- contract versions: `runtime_contract_version` and `extension_api_version`
- lifecycle hooks: `install`, `start`, `health_check`, `run`, and `shutdown`
- capability boundary: scopes, allowed tool calls, dangerous-action classes, secret requirements, network posture, and artifact I/O
- compatibility ranges: supported Aegis runtime range, extension API range, tool-registry range, and supported isolation tiers

The machine-readable schema is `schema/jsonschema/connector-manifest.schema.json`.

## Lifecycle hooks

Lifecycle hooks are descriptive contracts, not invitations to create a hidden orchestrator.

- `install` prepares immutable assets or validates local prerequisites
- `start` boots the extension runtime surface
- `health_check` proves the extension can still serve bounded work
- `run` performs the connector or processor's primary unit of work
- `shutdown` drains and releases extension-owned resources

Every hook declares a handler, timeout class, and idempotency expectation.

## Capability boundary

The capability boundary is the anti-footgun layer for extensions.

It declares:

- required scopes the caller must hold
- allowed built-in tools the extension may invoke
- dangerous-action classes the extension can participate in
- secret names the runtime may inject
- network mode and optional egress allowlist
- artifact input and output kinds

This keeps extension execution subordinate to runtime policy instead of letting manifests smuggle in broad privileges.

## Kind-specific interfaces

### Tool connectors

Tool connectors define one or more tool surfaces with:

- `tool_id`
- input and output schema refs
- executor kind
- mutating flag
- artifact expectations

### Artifact processors

Artifact processors define:

- accepted artifact kinds
- emitted artifact kinds
- processing mode
- maximum input size

This keeps artifact post-processing explicit and auditable instead of letting arbitrary processors attach themselves to replay state.

## Sample fixtures

- `tests/extensibility/fixtures/sample-connector.yaml`
- `tests/extensibility/fixtures/sample-artifact-processor.yaml`

These are contract fixtures for TS-014 and are intentionally small.

## Deferred to later Phase 10 tasks

- machine-checkable compatibility policy semantics beyond declared version ranges
- sample extension pack layout and review rubric
- detailed MCP adapter contract shape

The MCP adapter remains an external adapter boundary and is handled in `P10-T02`.
