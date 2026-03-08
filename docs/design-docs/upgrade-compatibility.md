# Upgrade Compatibility

## Purpose

This document defines the compatibility surface for PHASE-15.
It describes which runtime artifacts participate in version-skew policy and how
that policy is represented in machine-readable form.

## Canonical machine-readable artifacts

- `meta/compatibility-matrix.yaml`
- `meta/version-skew-rules.yaml`

## Compatibility subjects

PHASE-15 explicitly tracks compatibility for:

- runtime protocol envelopes
- event payload versions
- checkpoint payload versions
- worker contract versions
- policy catalog versions
- extension manifest versions

## Policy boundary

Compatibility is not the same as permanent backward compatibility.
The matrix defines:

- current supported versions
- supported skew windows
- explicit deny combinations

Unsupported combinations must fail validation before upgrade work proceeds.
