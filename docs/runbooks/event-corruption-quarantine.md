    # Event corruption or replay inconsistency

    ## Trigger

    seq gap, hash mismatch, or replay error

    ## Detection signals

    - events: checkpoint.restored
    - operator surface: `replay`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    quarantine the session and stop unsafe continuation

    ## Operator steps

    1. Quarantine immediately.
2. Compare checkpoint and event tail integrity.
3. Restore from replica/archive if available.

    ## Evidence to capture

    session id, offending seq_no, event ids, checkpoint id, restore attempt notes

    ## Exit condition

    session is either restored cleanly or remains quarantined with evidence
