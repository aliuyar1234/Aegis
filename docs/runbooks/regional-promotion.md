# Regional promotion

This runbook anchors PHASE-17 regional promotion work.

## Trigger

Use this during a bounded regional failover or evacuation drill after the source
region has been fenced.

## Steps

1. Confirm the standby region is eligible in the topology profile.
2. Verify restore and placement evidence is current.
3. Promote the standby region to authoritative status.
4. Verify checkpoints, approvals, and artifact lineage remain bounded and intact.
5. Export the regional evidence bundle for the drill.

## Never do this

- promote a non-eligible standby region
- accept split-brain ambiguity as a temporary state
- claim mobility succeeded without evidence export
