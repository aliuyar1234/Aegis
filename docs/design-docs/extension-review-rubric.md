# Extension review rubric

Use this rubric before admitting a third-party extension pack into the Aegis compatibility surface.

## Required checks

- manifest schemas validate cleanly
- lifecycle hooks are declared for install, start, health check, run, and shutdown
- capability boundaries are explicit for scopes, secrets, network, and artifact I/O
- compatibility ranges are bounded for runtime release, extension API, and tool-registry version
- no extension claims direct canonical writes, direct runtime-event emission, policy bypass, or outbox bypass
- MCP adapters stay external-tool adapters only
- sample extension pack layout exists and member manifests are reviewable
- sandbox-profile assignments exist for every admitted manifest
- certification level and governing policy bundle are explicit when public listing is requested
- docs and sample fixtures exist and are linked from `TS-014`

## Reviewer prompts

- Does this extension preserve session ownership and outbox-before-side-effects semantics?
- Are dangerous-action classes and approval requirements still enforced by the control plane rather than the extension?
- Is artifact processing explicit and auditable instead of becoming a hidden replay path?
- Would replay and operator inspection still make sense if the external system disappeared?
- Are compatibility claims narrow enough that future runtime changes can reject drift instead of guessing?

## Approval rule

If any required check fails, the extension pack is not admitted to the supported compatibility surface.
