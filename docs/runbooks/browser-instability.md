    # Browser instability or page/session drift

    ## Trigger

    page crash, disconnect, unstable DOM, failed navigation

    ## Detection signals

    - events: observation.browser_snapshot_added, action.failed
    - operator surface: `session-detail`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    reattach or restabilize before any further mutation

    ## Operator steps

    1. Inspect browser handle and last stable artifact.
2. Attempt reattach.
3. If mutating path certainty is unclear, escalate.

    ## Evidence to capture

    browser handle id, page ref, stable artifact id, failing selector/url, worker id

    ## Exit condition

    browser path reattaches or escalates without hidden mutation
