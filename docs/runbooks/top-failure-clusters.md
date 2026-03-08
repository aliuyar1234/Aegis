# Top failure clusters

This runbook anchors PHASE-16 fleet triage.

## Trigger

Use this when operators need to compare many sessions that share a failure signature
 instead of drilling one session at a time.

## Steps

1. Open the fleet triage surface and select a bounded cohort.
2. Compare the cohort against the committed capacity, placement, overload, isolation,
   and storage-growth reports.
3. Export the operator evidence bundle for the cohort.
4. Link the cohort summary to the relevant overload or isolation runbook if the signature
   is pressure-driven.
5. Escalate only after the evidence bundle shows the cluster is not explained by a
   known bounded policy response.

## Never do this

- rely on narrative summaries without the evidence bundle
- collapse unrelated wait reasons into one incident label
- export raw session payloads when a bounded evidence bundle is enough
