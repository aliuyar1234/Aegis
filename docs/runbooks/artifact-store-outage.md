    # Artifact store outage

    ## Trigger

    signed upload fails or registration cannot complete

    ## Detection signals

    - events: artifact.registered
    - operator surface: `session-detail`
    - runbook mapping source: `meta/failure-runbooks.yaml`

    ## Expected system behavior

    control plane may continue for non-artifact-critical work; evidence-sensitive steps may block

    ## Operator steps

    1. Check MinIO/S3 status and signed URL path.
2. Re-run artifact registration only when storage is healthy.

    ## Evidence to capture

    artifact id, object key, action id, worker id, storage error details

    ## Exit condition

    artifacts are either registered immutably or session is blocked explicitly
