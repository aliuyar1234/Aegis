# Change Policy

Use this file when deciding whether a code or contract change also requires docs, metadata, or generated artifact updates.

## If you change runtime state or lifecycle
Update:
- `docs/design-docs/runtime-model.md`
- `schema/checkpoints/session-checkpoint-v1.schema.json`
- `schema/jsonschema/operator-session-view.schema.json`
- relevant phase docs and tasks

## If you change events, replay semantics, or checkpoints
Update:
- `schema/event-catalog/events.yaml`
- `schema/event-catalog/index.yaml`
- `schema/event-payloads/`
- `docs/design-docs/event-replay-model.md`
- replay tests and phase gates

## If you change transport or cross-language contracts
Update:
- `schema/proto/`
- `buf.yaml` and `buf.gen.yaml`
- `schema/transport-topology.yaml`
- `docs/design-docs/transport-topology.md`
- `docs/design-docs/contracts-versioning.md`

## If you change policy or security behavior
Update:
- `../operations/security.md`
- `docs/design-docs/security-governance.md`
- `meta/rbac-roles.yaml`
- `meta/abac-attributes.yaml`
- `meta/dangerous-action-classes.yaml`
- related runbooks and threat models

## If you change phase order, task wiring, or acceptance
Update:
- `meta/current-phase.yaml` if phase state changed
- `meta/phase-gates.yaml`
- `work-items/task-index.yaml`
- `meta/acceptance-criteria.yaml`
- `meta/test-suites.yaml`
- regenerate docs with `python3 scripts/generate_docs.py`

## Generated artifacts

After any change to source metadata, run:

```bash
python3 scripts/generate_docs.py
python3 scripts/generate_docs.py --check
```

## Forbidden shortcuts

- “Code explains itself.”
- “We’ll update docs after the next phase.”
- “The change is obvious enough not to document.”

In Aegis, that is drift.
