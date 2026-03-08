# Launch observability review

Use this runbook when confirming that launch telemetry and alerts are ready for a
bounded customer pilot.

## Workflow

1. open `meta/launch-observability-baseline.yaml`
2. verify every required launch signal is covered by a dashboard or alert surface
3. confirm every launch surface references a current SLO profile and runbook
4. fail the review if any required signal is uncovered or undocumented
