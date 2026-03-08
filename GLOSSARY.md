# GLOSSARY.md

| Term | Meaning |
|---|---|
| Session | The primary runtime abstraction: a durable, live unit of AI work. |
| SessionKernel | The authoritative Elixir process that owns live session state. |
| Lease epoch | Monotonic ownership version used to reject stale owners and stale approvals. |
| Action | A requested unit of external work such as a browser step, tool call, or model invocation. |
| Execution ID | The unique identifier for one concrete attempt to run an action. |
| Outbox | Durable table used to publish committed intent after transaction commit. |
| Historical replay | A replay mode that consumes recorded events and artifacts without re-executing external systems. |
| Checkpoint | Structured snapshot of session state used to accelerate recovery and replay. |
| Artifact | Immutable blob such as screenshot, DOM snapshot, browser trace, or raw output stored in object storage. |
| Capability token | Scope-limited credential used to authorize an effectful action execution. |
| Uncertain side effect | A state where the runtime cannot prove whether a write happened and must surface that uncertainty. |
| Operator takeover | Mode where a human temporarily controls the session or browser path. |
| Policy gate | Evaluation boundary that classifies actions as allow, constrained, require approval, or deny. |
| Tier A/B/C | Shared, isolated-execution, and dedicated multitenancy isolation tiers. |
| Control plane | Elixir-owned runtime truth and orchestration layer. |
| Execution plane | Python and Rust workers that perform external work without owning truth. |
| Data plane | External systems and environments that Aegis acts against. |
