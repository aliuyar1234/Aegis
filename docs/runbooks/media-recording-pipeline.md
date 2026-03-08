    # Media recording pipeline degradation

    ## Trigger

    Recording segmentation, manifest assembly, or signed-upload handoff is degraded for a voice/media session.

    ## Detection signals

    - events: `artifact.registered`, `health.degraded`
    - sidecar signal: recorder backlog or upload handoff delay
    - operator surface: `session-detail`
    - topology source: `tests/media/fixtures/sample-media-topology.yaml`

    ## Expected system behavior

    Recording status becomes explicit, artifact gaps are visible, and the runtime can fall back to transcript-plus-artifact replay instead of pretending the recording path is complete.

    ## Operator steps

    1. Verify whether the recorder sidecar is healthy, degraded, or draining.
    2. Confirm whether the issue is encoding backlog, signed-upload handoff delay, or storage pressure.
    3. Decide whether to continue with lower-fidelity recording, artifact-only fallback, or operator handoff.

    ## Evidence to capture

    session id, recorder sidecar id, latest manifest artifact id, missing segment window, active retention class

    ## Exit condition

    Recorder backlog is cleared and new artifacts are arriving normally, or the session is explicitly operating in fallback mode with the gap documented.
