    # Approval timeout

    ## Trigger

    approval expired before decision

    ## Detection signals

    - events: approval.expired
    - operator surface: `approvals-queue`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    action stays blocked; default deny or escalation path follows policy

    ## Operator steps

    1. Inspect approval request, expiry, and risk class.
2. Decide whether to deny, extend, or re-request under policy.

    ## Evidence to capture

    approval id, action hash, expires_at, operator queue state

    ## Exit condition

    approval state is explicit and session leaves waiting state correctly
