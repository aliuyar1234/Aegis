# Launch exception response

Use this runbook when a bounded pilot launch exception occurs.

## Workflow

1. classify the exception from `meta/launch-exception-governance.yaml`
2. obtain the required approval path for the exception class
3. execute the containment or rollback boundary
4. attach the resulting evidence before resuming the pilot
