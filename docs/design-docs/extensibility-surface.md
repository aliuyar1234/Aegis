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

### MCP adapters

MCP adapters are explicitly edge adapters.

They define:

- external MCP server transport and reference
- session binding that proves Aegis still owns dispatch and worker-event flow
- tool translation from external MCP tools into Aegis-facing tool ids
- protocol-boundary flags that stay fixed to `false` for runtime-protocol takeover, direct event emission, direct canonical writes, policy bypass, and outbox bypass

Their dedicated boundary doc is `docs/design-docs/mcp-adapter-boundary.md`.

## Sample fixtures

- `tests/extensibility/fixtures/sample-connector.yaml`
- `tests/extensibility/fixtures/sample-artifact-processor.yaml`
- `tests/extensibility/fixtures/sample-mcp-adapter.yaml`
- `tests/extensibility/fixtures/sample-extension-pack/pack.yaml`

These are contract fixtures for TS-014 and are intentionally small.

## Compatibility policy

Third-party extensions are governed by the machine-readable policy in `meta/extension-compatibility-policy.yaml`.

The policy requires:

- bounded compatibility ranges
- explicit lifecycle and capability boundaries
- review-rubric coverage
- sample extension-pack evidence
- MCP remaining an external adapter boundary

The prose companion is `docs/design-docs/extension-compatibility-policy.md`.

## Sample extension pack and review

The sample pack fixture under `tests/extensibility/fixtures/sample-extension-pack/` demonstrates the minimum reviewable package layout for a third-party extension bundle.

The review rubric is `docs/design-docs/extension-review-rubric.md`.

## Remaining later Phase 10 work

Only packaging polish beyond the sample pack is left for later phases.
