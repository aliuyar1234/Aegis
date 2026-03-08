    # System or session degraded mode

    ## Trigger

    health.degraded surfaced in runtime or control plane

    ## Detection signals

    - events: health.degraded
    - operator surface: `session-fleet`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    admission may be restricted; operator sees explicit degraded reason

    ## Operator steps

    1. Identify whether degradation is local, session-scoped, or system-wide.
2. Delay new risky work if the control plane is unstable.

    ## Evidence to capture

    health scope, reason, affected sessions, dependency status

    ## Exit condition

    system returns healthy or remains explicitly degraded
