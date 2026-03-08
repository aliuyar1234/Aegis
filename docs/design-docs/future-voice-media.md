# Future voice/media expansion path

Voice and media are not the first wedge, but the repository now treats them as a real future phase rather than a placeholder.

## Phase-11 outputs

- media/topology contracts
- Rust sidecar boundaries
- voice/media phase gate
- operator/runbook deltas for degraded QoS and handoff
- isolation pool guidance
- future session-state and operator-view stubs

## Rules that do not change

- session remains primary
- one authoritative owner remains mandatory
- replay still consumes recorded outputs and artifacts
- sidecars stay out-of-process

## Contract surfaces

Phase 11 defines concrete future stubs for:

- Rust sidecar contracts in `docs/design-docs/media-sidecar-contracts.md`
- media session-state extensions in `docs/design-docs/media-session-extensions.md`
- future operator-console deltas in `docs/design-docs/media-operator-surfaces.md`
- media topology and degraded-mode policy in `docs/design-docs/media-topology.md`

These are bounded design assets, not live telephony implementation.

## Boundary commitments

- Rust sidecars handle packets, codecs, bridging, and recording hot paths
- Elixir keeps session ownership, replay semantics, policy, approvals, and operator control
- replay remains transcript- and artifact-based rather than packet-based
- QoS degradation and operator handoff stay explicit in session state
- capacity isolation remains compatible with shared, tenant-isolated, and dedicated pool classes
