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
