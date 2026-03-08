# Service-scale support review

Use this runbook when confirming that Aegis can support more than one post-pilot
customer at a time.

## Workflow

1. open `meta/service-scale-operations-readiness.yaml`
2. confirm each service-scale cadence maps to a committed owning rotation
3. verify the required communication and observability refs are current
4. fail the review if service-scale coverage still depends on founder-only support
