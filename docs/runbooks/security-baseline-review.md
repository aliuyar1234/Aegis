# Security baseline review

Use this runbook when reviewing the minimum security launch controls for Aegis.

## Workflow

1. open `meta/security-baseline-manifest.yaml`
2. verify every required control has an owner and committed doc references
3. confirm the launch-ready controls still map to current operational docs
4. fail the review if any required control is missing or undocumented

## Do not do this

- do not waive a required launch control silently
- do not rely on oral knowledge for key rotation or secret handling
