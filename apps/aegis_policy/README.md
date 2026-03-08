# aegis_policy

## Purpose

Policy, tool registry, approvals

## Responsibilities

- tool descriptors
- risk classification
- dangerous-action defaults
- approval and capability token issuance

## Current source of truth

- canonical catalog: `schema/tool-registry.yaml`
- dangerous-action catalog: `meta/dangerous-action-classes.yaml`
- descriptor schema: `schema/jsonschema/tool-descriptor.schema.json`
- Elixir boundaries: `Aegis.Policy.ToolRegistry`, `Aegis.Policy.DangerousActionCatalog`,
  `Aegis.Policy.Evaluator`, `Aegis.Policy.CapabilityToken`
- policy evaluator: `Aegis.Policy.Evaluator`
- validation/test entrypoint: `python3 scripts/run_policy_suite.py`

## Must not own

- hidden authoritative state outside the assigned boundary
- logic that belongs to another app just because it is convenient

## First implementation note

When adding code here, link the module or boundary to the relevant phase doc, ADR, acceptance criteria, and tests.
