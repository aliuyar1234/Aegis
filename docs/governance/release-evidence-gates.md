# Release Evidence Gates

## Purpose

PHASE-15 introduces release evidence as a first-class artifact rather than an informal
checklist.

## Evidence categories

- compatibility matrix coverage
- version-skew rule coverage
- rolling-upgrade artifact coverage
- restore-drill and recovery-objective coverage
- standby-promotion gate coverage

## Policy boundary

This document does not claim that release automation is complete.
It defines the gateable evidence surface the runtime must eventually require before
candidate releases are considered safe.
