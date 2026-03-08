# scripts/

These scripts validate and bootstrap the handoff repository.

## Scripts

- `bootstrap.sh` — create a Python virtualenv and install validator dependencies
- `smoke.sh` — run validators and check local compose configuration
- `validate_repo.py` — required files, anti-drift phrases, AGENTS size, basic repo integrity
- `validate_schemas.py` — JSON Schema and event-catalog validation, proto sanity checks
- `validate_traceability.py` — invariants/ADRs/tasks/tests/acceptance coherence
- `next_tasks.py` — print currently unblocked tasks

These scripts are intentionally lightweight and agent-legible.
