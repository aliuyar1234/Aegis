# aegis_browser_worker

## Purpose
browser automation worker for the first wedge

## Phase 08 surface
- opens read-only or effectful browser contexts
- navigates and inspects visible state
- executes approval-bound browser writes for fixture-driven submit flows
- captures before/after screenshots, DOM evidence, and trace artifacts
- returns resumable browser handle metadata plus a checkpoint-friendly recovery bundle
- marks uncertain writes for operator takeover instead of silently retrying

## Skeleton modules
- `worker.py` exposes the browser worker facade
- `dispatch.py` handles fixture-oriented dispatch inputs
- `lifecycle.py` owns the Playwright lifecycle boundary
- `runner.py` executes fixture-driven read-only and effectful workflows

## Must not do
- own authoritative session state
- write canonical runtime tables
- bypass capability tokens or policy decisions
