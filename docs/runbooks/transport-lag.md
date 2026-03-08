    # JetStream lag or dispatch transport degradation

    ## Trigger

    consumer lag, redelivery spikes, or missed accept deadlines

    ## Detection signals

    - events: action.heartbeat_missed
    - operator surface: `session-fleet`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    stop treating transport as healthy; do not hide latency as worker success

    ## Operator steps

    1. Check stream lag and consumer health.
2. Inspect redelivery counts and ack waits.
3. Pause risky admissions if lag is severe.

    ## Evidence to capture

    stream name, consumer name, lag metrics, redelivery counts, affected execution ids

    ## Exit condition

    transport returns healthy or sessions move to degraded/uncertain mode
