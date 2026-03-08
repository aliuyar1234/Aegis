    # Lease ambiguity / fencing

    ## Trigger

    owner cannot prove lease or partition prevents renewals

    ## Detection signals

    - events: system.lease_lost, health.degraded
    - operator surface: `session-detail`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    current owner self-fences and stops side effects

    ## Operator steps

    1. Inspect fenced/degraded markers.
2. Prevent manual retries until lease is stable.
3. Resume only after one node owns the next epoch.

    ## Evidence to capture

    session id, owner node, lease epoch, transport status, DB status

    ## Exit condition

    exactly one owner resumes or session remains safely paused
