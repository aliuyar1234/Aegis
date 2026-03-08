    # Worker crash or lost worker heartbeat

    ## Trigger

    missed worker heartbeat, lost ActionAccepted follow-up, or runtime event `system.worker_lost`

    ## Detection signals

    - events: system.worker_lost, action.heartbeat_missed
    - operator surface: `session-detail`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    mark active execution orphaned or uncertain; do not let worker become source of truth

    ## Operator steps

    1. Inspect session detail owner, action, and deadlines.
2. Check whether the action was effectful.
3. Retry only if tool idempotency and policy allow it.
4. If effectful certainty is unclear, escalate to human review.

    ## Evidence to capture

    session id, action id, execution id, worker id, last heartbeat, artifact refs, policy decision

    ## Exit condition

    session resumes, escalates, or fails with explicit uncertainty marker
