# Policy decision model

Policy is part of runtime correctness.

## Decision classes

A policy evaluation produces exactly one of:
- `allow`
- `allow_with_constraints`
- `require_approval`
- `deny`

## Required policy inputs

- tenant / workspace
- session mode and health
- tool descriptor and version
- action kind and risk class
- dangerous action class
- data sensitivity
- prior failures or uncertainty markers
- target environment
- requested argument digest

## Tool descriptor source of truth

Tool descriptors live in `schema/tool-registry.yaml` and each descriptor must
validate against `schema/jsonschema/tool-descriptor.schema.json`.

## Required policy outputs

- decision class
- constraints (if any)
- action hash
- lease epoch seen during evaluation
- approval requirement / expiry
- evidence requirements

## Browser mutation rule

Dangerous browser mutations are high-risk by default and must not dispatch until:
1. policy has produced a non-deny decision,
2. approval requirements have been met,
3. a scoped capability token has been minted,
4. the execution attempt carries the approved argument digest.

## Default browser write classes

- `browser_write_low` defaults to `allow_with_constraints` and still requires a scoped capability token.
- `browser_write_medium` defaults to `require_approval` and binds the approval to the exact action hash and lease epoch.
- `browser_write_high` defaults to `deny` unless a later explicit policy surface says otherwise.
