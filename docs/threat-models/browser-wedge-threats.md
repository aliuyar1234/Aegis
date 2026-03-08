# Browser wedge threats

## Wedge-specific risks

- accidental browser writes without approval
- browser context leakage between tenants
- untrusted page content influencing prompt or action assembly
- screenshots or DOM snapshots containing restricted data
- operator takeover bypassing policy boundaries
- uncertain writes after browser worker crash
- credential leakage into browser automation logs

## Controls

- browser writes default to higher-risk class
- browser contexts are tenant-scoped and not reused across tenants
- raw artifacts carry sensitivity and retention metadata
- operator takeover is a mode change in the timeline
- capability tokens scope allowed action and arguments
- uncertain side effects escalate to human review
- worker logs must avoid raw secrets and use redaction hooks
