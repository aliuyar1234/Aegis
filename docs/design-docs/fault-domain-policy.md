# Fault-domain policy

## Purpose

Fault domains in Aegis are not incidental infrastructure labels. They are runtime
inputs that affect placement, evacuation, and promotion safety.

## Required semantics

- every fault domain belongs to a concrete region
- every fault domain declares its role
- standby eligibility is explicit
- supported tenant tiers are explicit

## Why this matters

Without a fault-domain catalog, regional placement and evacuation become folklore.
That is precisely what PHASE-17 is preventing.
