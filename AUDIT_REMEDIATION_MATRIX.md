# AUDIT_REMEDIATION_MATRIX.md

| Audit finding | Severity | Fix status | Files changed | Remaining caveat |
|---|---|---|---|---|
| PHASE-00 still planned / wrong start task | Critical | Fixed | `meta/current-phase.yaml`, `work-items/task-index.yaml`, `scripts/next_tasks.py`, `AGENTS.md`, `README.md` | None |
| Contradictory phase graph | Critical | Fixed | `meta/phase-gates.yaml`, phase docs, task refs | None |
| Browser phase required capability tokens too early | Critical | Fixed | `work-items/task-index.yaml`, `PHASE-05*`, `PHASE-07*`, `PHASE-08*`, browser fixtures | None |
| Transport boundary under-specified | Critical | Fixed | `docs/design-docs/transport-topology.md`, `schema/transport-topology.yaml`, `buf.*`, `scripts/generate_contracts.sh` | None |
| Event/checkpoint surface too loose | Critical | Fixed | `schema/event-payloads/`, `schema/checkpoints/`, `schema/event-catalog/*`, validators | None |
| Phase gates were prose-only | Critical | Fixed | `tests/phase-gates/*.yaml`, `scripts/run_phase_gate.py`, CI workflows | None |
| Test paths/commands incoherent | High | Fixed | `meta/test-suites.yaml`, `test/`, `tests/`, `TEST_STRATEGY.md` | Runtime implementation tests remain scaffolded by design |
| Acceptance criteria phase-leaky / weak | High | Fixed | `meta/acceptance-criteria.yaml`, phase docs, `ACCEPTANCE_CRITERIA.md` | None |
| Operator/session projection contracts incomplete | High | Fixed | Protobufs, JSON Schemas, `docs/design-docs/projection-model.md`, `docs/product-specs/operator-console.md` | None |
| Security/policy too prose-heavy | High | Fixed | security catalogs, JSON Schemas, `SECURITY.md`, `docs/design-docs/security-governance.md` | None |
| Validators too shallow | High | Fixed | `scripts/validate_repo.py`, `scripts/validate_schemas.py`, `scripts/validate_traceability.py`, `scripts/generate_docs.py` | None |
| Local dev bootstrap incomplete / OTEL mismatch | High | Fixed | `infra/local/*`, `scripts/init_local.sh`, `Makefile` | Docker still required for local stack |
| Later phases too thin | High | Fixed | phase docs 10–13, acceptance, tasks, prompts, phase gates | None |
| Runbooks too shallow | Medium | Fixed | `docs/runbooks/*.md`, `meta/failure-runbooks.yaml` | None |
| Generated artifacts could drift silently | Medium | Fixed | `scripts/generate_docs.py`, `meta/generated-files.yaml`, CI workflows | None |
| Runtime heartbeat subject existed without matching proto contract | High | Fixed in v3 | `schema/proto/aegis/runtime/v1/worker.proto`, `schema/transport-topology.yaml`, `docs/design-docs/transport-topology.md`, `infra/local/init-nats.sh` | None |
| Cancel-path consumer coverage was implicit | High | Fixed in v3 | `schema/transport-topology.yaml`, `infra/local/init-nats.sh`, `scripts/validate_schemas.py`, `tests/transport/test_transport_topology.py` | None |
| Phase gates were typed too loosely to serve as strong execution contracts | High | Fixed in v3 | `schema/jsonschema/phase-gate.schema.json`, `tests/phase-gates/*.yaml`, `scripts/run_phase_gate.py`, `TEST_STRATEGY.md` | Phase gates remain contract-level gates, not a live implementation runner |
| Checkpoint/browser fixture schemas still left failure-sensitive fields under-typed | Medium | Fixed in v3 | `schema/checkpoints/session-checkpoint-v1.schema.json`, `schema/jsonschema/browser-workflow-fixture.schema.json`, `tests/browser_e2e/fixtures/*`, `tests/browser_e2e/test_browser_fixture_semantics.py` | None |
| Bundle shipped cache/noise artifacts that do not belong in SSOT handoff repos | Medium | Fixed in v3 | `.gitignore`, `meta/repo-checks.yaml`, bundle contents | None |
| Elixir protobuf consumption strategy was implied but not explicit | Medium | Fixed in v3 | `schema/proto/README.md`, `docs/design-docs/contracts-versioning.md` | Elixir library choice remains implementation-time, not architecture-time |
