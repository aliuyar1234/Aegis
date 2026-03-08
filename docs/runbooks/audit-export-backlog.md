# Audit export backlog

## When to use

Use this runbook when enterprise audit exports stop completing within the bounded SLO or when evidence bundles are missing expected timeline or artifact metadata.

## Signals

- audit export bundle preparation breaches the defined SLO
- export destination delivery retries accumulate
- signed-url evidence packaging fails or expires before retrieval
- operator-facing audit export surface shows backlog or degraded status

## Immediate checks

- confirm tenant, workspace, session, and export request scope
- confirm artifact records still carry `redaction_state` and `retention_class`
- confirm destination-specific credentials or workload identity remain valid
- confirm object-store evidence can still be rehydrated through signed URLs

## Containment

- pause automatic export retries if duplicate delivery would confuse evidence consumers
- preserve the pending export request and timeline hashes as evidence
- notify the bounded audit roles rather than widening access ad hoc

## Recovery

- restore destination access or signed-url generation
- rebuild the export bundle from recorded events and artifact metadata
- verify redacted records remain marked as redacted stubs
- record operator notes and export recovery outcome in the incident trail
