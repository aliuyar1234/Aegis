# Real infrastructure proving

This document defines the production-like proving surface that must exist before
Aegis is treated as ready for a bounded design-partner launch.

## Required proving areas

- backup and PITR restore proof
- rollback proof
- rolling-upgrade proof
- tenant-isolation proof

## Constraint

Repo-native evidence is not enough on its own.
The proving surface must bind committed runbooks and evidence references to explicit
production-like environments.
