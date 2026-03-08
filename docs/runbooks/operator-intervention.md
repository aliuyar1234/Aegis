    # Operator intervention or manual takeover

    ## Trigger

    operator joined, paused, requested abort, took control, or returned control

    ## Detection signals

    - events: operator.joined, operator.paused, operator.abort_requested, operator.took_control, operator.returned_control
    - operator surface: `session-detail`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    autonomous dispatch pauses while operator is authoritative

    ## Operator steps

    1. Confirm control mode changed.
2. Capture operator notes and artifacts.
3. Resume only with explicit return-control event.

    ## Evidence to capture

    operator id, session id, takeover start/end, notes, artifacts

    ## Exit condition

    session remains timeline-complete and resumable
