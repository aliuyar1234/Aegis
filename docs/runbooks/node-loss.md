    # Owner node loss

    ## Trigger

    lease renewal stops and session enters adoption path

    ## Detection signals

    - events: system.lease_lost, system.node_recovered
    - operator surface: `session-detail`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    another node may adopt only after lease expiry; stale owner must not dispatch

    ## Operator steps

    1. Confirm `system.lease_lost` then `system.node_recovered`.
2. Verify adoption target node and lease epoch.
3. Confirm no silent duplicate side effects.

    ## Evidence to capture

    session id, old/new owner node, lease epoch, last checkpoint id, in-flight action ids

    ## Exit condition

    one owner remains and session state is hydrated or quarantined
