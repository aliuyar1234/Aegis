# Reference deployment tracks

This document defines the PHASE-19 reference deployment-track surface.

## Goal

Turn deployment guidance into explicit tracks that bind together the already implemented
flavor, topology, SLO, and public ecosystem surfaces.

## What a track captures

Each track is a bounded rollout lane, not a free-form architecture recommendation.
Tracks identify:

- deployment flavor
- standby or regional topology surface
- SLO profile
- compatible public ecosystem track
- required evidence bundles
- runbook set

The machine-readable source is `meta/reference-deployment-tracks.yaml`.

## Why this matters

By PHASE-19, Aegis already has packaging, restore, fleet, regional, and ecosystem evidence.
Reference tracks prevent adopters from having to rediscover which pieces belong together.

## Non-goal

These tracks are not a promise that every possible topology is supported.
They describe the supported and reviewable adoption lanes the repo is ready to stand behind.
