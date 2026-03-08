    # Media QoS degradation

    ## Trigger

    Voice/media session QoS is degraded long enough that operator visibility or handoff is required.

    ## Detection signals

    - events: `health.degraded`
    - sidecar signal: packet loss or jitter exceeds bounded profile
    - operator surface: `session-detail`
    - contract source: `tests/media/fixtures/sample-media-session-extension.yaml`

    ## Expected system behavior

    QoS degradation is explicit in session state, capacity isolation remains visible, and the operator sees a concrete handoff recommendation. The system does not silently keep the session in an apparently healthy state.

    ## Operator steps

    1. Confirm which media sidecar is degraded and whether the issue is isolated to one tenant pool or system-wide.
    2. Review the current QoS level, degradation reason, and recording status.
    3. Decide whether to continue in degraded mode, pause risky recording work, or take operator handoff.

    ## Evidence to capture

    session id, sidecar ids, pool class, QoS level, degradation reason, latest transcript or recording manifest refs

    ## Exit condition

    QoS returns to healthy, or the session remains explicitly marked as handoff-required with an operator-owned next action.
