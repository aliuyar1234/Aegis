# Retention backlog

## When to use

Use this runbook when archival movement, restore latency, or redaction completion drifts beyond the bounded enterprise SLOs.

## Signals

- archive queues or object-store lifecycle transitions fall behind policy
- archived artifact restore breaches the restore objective
- redaction completion breaches the bounded response window
- customer artifact or long-lived audit event classes stop following their policy class

## Immediate checks

- confirm which retention class is affected
- confirm the affected tenant, workspace, and artifact/session scope
- confirm redaction state is still represented in metadata
- confirm timeline history has not been rewritten or dropped for retention convenience

## Containment

- freeze destructive cleanup for the affected class until policy drift is understood
- prioritize long-lived audit events and redacted payload stubs over debug artifact cleanup
- expose degraded retention status to operators instead of hiding backlog

## Recovery

- drain the affected archive or redaction backlog in retention-class order
- verify archive index integrity before declaring restore healthy
- re-check the relevant SLO surface against the policy targets
- attach the recovery summary to the enterprise evidence trail
