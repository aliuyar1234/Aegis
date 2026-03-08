# Regional evacuation

This runbook anchors PHASE-17 regional evacuation work.

## Trigger

Use this when a primary region must be evacuated due to control-plane loss, compliance
pressure, or a bounded regional promotion drill.

## Steps

1. Confirm the topology profile and source/target regions.
2. Fence the source region before promotion.
3. Verify restore evidence and continuity prerequisites.
4. Switch placement policy to the target region.
5. Promote the target region and verify single-owner behavior.

## Never do this

- promote a standby region without fencing the source region
- skip approval or artifact continuity checks
- improvise new regional routes outside the committed topology profile
