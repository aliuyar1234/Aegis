# What good looks like

## Good task completion
- task implementation is bounded
- linked ADRs were read
- tests and acceptance IDs are updated
- docs changed when boundaries changed
- no hidden source of truth appeared

## Good event definition
- semantically meaningful
- tied to a session
- small payload with references to artifacts for bulk data
- deterministic/nondeterministic boundary is explicit
- operator can understand why it exists

## Good recovery behavior
- owner loss is visible
- duplicate side effects are not hidden
- session can hydrate from checkpoint + tail
- operator can see whether a write is certain, uncertain, or denied

## Good docs
- specific to Aegis
- cross-linked
- independent of outside context
- task/acceptance/test traceability exists
