# Production-like proving

Use this runbook when executing the production-like proving wave for Aegis before
design-partner launch.

## Workflow

1. choose the proving environment from `meta/real-infrastructure-proving.yaml`
2. confirm the referenced restore and upgrade drills are current
3. confirm the referenced release and lifecycle evidence is current
4. execute the proving sequence and retain the resulting evidence links
5. fail the proving pass if rollback, restore, upgrade, or isolation proof is missing

## Do not do this

- do not substitute repo-only evidence for production-like proving
- do not mark a proving environment ready if its isolation or rollback evidence is missing
