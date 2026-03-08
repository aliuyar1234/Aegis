# Operator exercises

This document defines the PHASE-19 operator training and incident exercise surface.

## Goal

Make operator training explicit and evidence-linked so operational readiness is not a hand-waved human process.

## Exercise shape

Each exercise declares:

- a bounded scenario type
- runbook references
- required evidence prerequisites
- expected outcomes

The machine-readable source is `meta/operator-exercise-manifest.yaml`.

## Why exercises exist

Operator confidence is part of runtime correctness in Aegis.
If operators cannot rehearse approval escalation, regional failover, or extension revocation
against committed evidence and runbooks, the system is still too dependent on its authors.

## Constraint

Exercises are not new runtime semantics.
They are structured adoption overlays built on already implemented phases.
