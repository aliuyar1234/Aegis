# work-items/

This directory contains the machine-readable execution plan.

## Rules

- Tasks are the smallest bounded units Codex should target in one focused run.
- Every task must reference ADRs, acceptance criteria, and tests.
- Critical-path tasks should not be skipped because adjacent tasks look easier.
- Update task metadata when a task meaningfully changes scope or prerequisites.

Use `scripts/next_tasks.py` to print currently unblocked tasks.
