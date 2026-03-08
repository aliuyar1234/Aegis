# Acceptance Criteria

The canonical machine-readable source is `meta/acceptance-criteria.yaml`.
This file explains how to use those criteria.

## Rules

- Acceptance criteria are **phase-specific**. A phase may contribute prerequisites for later phases, but it is not complete until its own criteria pass.
- Generic hygiene criteria are **not** valid substitutes for product or runtime completion.
- Demo gates are real gate artifacts under `tests/phase-gates/`, not prose-only narratives.
- A task is not done unless the linked tests and acceptance criteria are updated together.

## Phase summary

- PHASE-00: repo, bootstrap, generated artifact freshness
- PHASE-01: session lifecycle, supervisor ownership, projection boundary
- PHASE-02: append/outbox atomicity, checkpoint schema, replay correctness, event payload coverage
- PHASE-03: single owner, adoption, self-fencing
- PHASE-04: transport topology, execution bridge, contract generation, trace propagation, worker DB boundaries
- PHASE-05: browser baseline, artifact metadata, resumable handles, workflow fixtures
- PHASE-06: operator session view, replay surfaces, intervention events, runbook-linked surfaces
- PHASE-07: tool descriptors, policy decisions, approval binding, capability tokens, dangerous-action defaults
- PHASE-08: effectful browser flows, uncertainty handling, chaos coverage, demo gates
- PHASE-09: tenancy tiers, quotas, authz, audit/redaction
- PHASE-10: connector SDK and compatibility policy
- PHASE-11: voice/media path contracts and gates
- PHASE-12: OSS/managed split outputs
- PHASE-13: enterprise controls and readiness gate
- PHASE-14: replay oracle, determinism taxonomy, simulation DSL, contract conformance, replay diffing, benchmark scorecards, and fixture authoring flow
- PHASE-15: compatibility windows, upcasters, rolling upgrades, restore drills, standby promotion, and release evidence
- PHASE-16: capacity/SLO policy, deterministic placement, overload doctrine, noisy-neighbor isolation, storage-scaling evidence, and fleet triage bundles
- PHASE-17: regional topology profiles, region-aware placement, evacuation drills, session mobility continuity, and regional evidence bundles
- PHASE-18: extension certification levels, sandbox profiles, policy bundles, public compatibility tracks, and ecosystem evidence bundles
- PHASE-19: adoption profiles, reference deployment tracks, operator drills, golden-path starter kits, and adoption evidence bundles
- PHASE-20: operator accreditation, rollout-wave governance, incident-review packets, deprecation discipline, and lifecycle evidence bundles

Read `meta/acceptance-criteria.yaml` for the exact statements and linked tests.
