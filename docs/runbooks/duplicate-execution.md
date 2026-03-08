    # Duplicate execution or duplicate terminal callback

    ## Trigger

    duplicate completion/failure observed for same execution/action

    ## Detection signals

    - events: action.succeeded, action.failed
    - operator surface: `replay`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    dedupe at action ledger; surface uncertainty if external effect already happened

    ## Operator steps

    1. Inspect duplicate markers in replay.
2. Confirm dedupe key and terminal state chosen.
3. Escalate if effectful ambiguity exists.

    ## Evidence to capture

    session id, action id, execution id, duplicate event ids, result artifacts

    ## Exit condition

    single terminal truth remains and duplicate is visible in timeline
