# aegis_browser_worker

## Purpose
browser automation worker for the first wedge

## Phase 05 baseline
- opens a read-only browser context
- navigates and inspects visible state
- captures screenshot, DOM snapshot, and trace evidence through artifact metadata
- returns resumable browser handle metadata plus a checkpoint-friendly recovery bundle
- rejects mutating fixture steps such as `click`, `fill`, and `submit`

## Skeleton modules
- `worker.py` exposes the browser worker facade
- `dispatch.py` handles read-only dispatch inputs
- `lifecycle.py` owns the Playwright lifecycle boundary
- `runner.py` executes fixture-driven read-only workflows

## Must not do
- own authoritative session state
- write canonical runtime tables
- bypass capability tokens or policy decisions
