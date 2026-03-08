# scripts/

These scripts validate, bootstrap, and exercise the Aegis repository.

## Scripts

- `bootstrap.py` - create a Python virtualenv and install validator dependencies in a cross-platform way
- `init_local.py` - initialize the official local evaluation stack and replay SQL migrations into dev/test databases
- `smoke.py` - run validators and check local compose configuration in a cross-platform way
- `validate_repo.py` - required files, anti-drift phrases, AGENTS size, basic repo integrity
- `validate_schemas.py` - JSON Schema and event-catalog validation, proto sanity checks
- `validate_traceability.py` - invariants/ADRs/tasks/tests/acceptance coherence
- `next_tasks.py` - print currently unblocked tasks
- phase-specific `run_phaseXX_*.py` scripts - emit machine-checkable validation reports for phase surfaces
- phase-specific `build_phaseXX_*_evidence.py` scripts - assemble reproducible evidence bundles from committed reports

These scripts are intentionally lightweight and agent-legible.
