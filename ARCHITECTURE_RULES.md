# ARCHITECTURE_RULES.md

This file converts the thesis into reviewable implementation rules.

## Rule set

1. **One owner, one session.** No alternative authority paths.
2. **No worker writes to canonical tables.**
3. **No effectful dispatch before commit + outbox.**
4. **No large binary blobs in canonical event payloads.**
5. **No hidden side effects outside the timeline.**
6. **No dangerous browser writes without explicit policy evaluation.**
7. **No implicit contract drift across Elixir/Python/Rust.**
8. **No hot-path NIFs for media/protocol/recording work.**
9. **No replay mode that silently re-executes external systems.**
10. **No UI-only state transitions for approvals or operator control.**

## Doc-change triggers

Any change to these areas requires doc updates:

- session lifecycle → `docs/design-docs/runtime-model.md`
- event envelope or event types → `schema/event-catalog/events.yaml` and `docs/design-docs/event-replay-model.md`
- transport/contracts → `schema/proto/`, `schema/jsonschema/`, `docs/design-docs/contracts-versioning.md`
- policy boundaries → `docs/design-docs/security-governance.md`, `SECURITY.md`, related runbooks
- wedge scope → `docs/product-specs/browser-ops-wedge.md`
- phase sequencing → `docs/exec-plans/active/`, `work-items/`, `meta/phase-gates.yaml`

## Review posture

If a change cannot be explained in terms of session truth, operator trust, recovery, or policy boundaries, it is probably the wrong change.
