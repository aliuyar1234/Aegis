# PHASE-26 - Live customer operations, release automation, and field evidence governance

**Status:** current

## Phase goal

Turn the PHASE-25 GA-ready posture into an explicit SSOT program for operating live
customer fleets, automating release motion, capturing field evidence, and governing
post-GA lifecycle decisions.

## Why this phase exists

PHASE-25 proved that Aegis can define a credible GA transition and repeatable customer
rollout. The next gap is what happens after that decision: live customer operations,
release automation, field reliability evidence, and lifecycle governance can no longer
depend on manual founder coordination or ad hoc customer memory.

## Scope

- live customer operating cadence across multiple active customers
- release automation and governed change motion
- field evidence and customer reliability corpus
- post-GA lifecycle and compatibility governance
- post-GA operating review gate

## Non-goals

- broad self-serve productization
- commercial packaging or pricing changes
- replacing runtime proof with anecdotal customer stories
- generic workflow-builder expansion unrelated to live operations
- managed-cloud automation beyond committed release and operating governance

## Prerequisites

PHASE-23, PHASE-24, and PHASE-25

## Deliverables

- live customer operations program definition
- release automation and change-governance surface
- field evidence and customer reliability corpus surface
- post-GA lifecycle governance surface
- post-GA operating review gate definition

## Detailed tasks

- `P26-T01` - Define the live customer operations program for post-GA customer fleets
- `P26-T02` - Define the automated release and governed change surface
- `P26-T03` - Define the field evidence and customer reliability corpus
- `P26-T04` - Define post-GA lifecycle and compatibility governance
- `P26-T05` - Gate post-GA operations on live-ops, release automation, field evidence, and lifecycle governance

## Dependencies

- prerequisites: PHASE-23, PHASE-24, PHASE-25
- unlocks after exit: none yet

## Risks

- treating GA as the end of operational design instead of the start of live service obligations
- allowing release motion to drift back into manual founder judgment
- losing reliability learnings because field evidence is not captured as committed SSOT

## Test plan

- `TS-079` - Live customer operations planning validation
- `TS-080` - Release automation planning validation
- `TS-081` - Field evidence corpus planning validation
- `TS-082` - Post-GA lifecycle governance planning validation
- `TS-083` - Post-GA operating review gate planning validation

## Acceptance criteria

- `AC-119` - PHASE-26 defines an explicit live customer operations program for post-GA fleets, including bounded operating cadences, customer classes, and operational handoff rules.
- `AC-120` - PHASE-26 defines an automated release and governed change surface that binds release motion, rollback expectations, and review checkpoints instead of manual founder sequencing.
- `AC-121` - PHASE-26 defines a field evidence and customer reliability corpus so incidents, support signals, and rollout learnings are captured as explicit evidence rather than anecdotal memory.
- `AC-122` - PHASE-26 defines post-GA lifecycle and compatibility governance for live customers so upgrades, deprecations, and compatibility promises remain bounded and reviewable.
- `AC-123` - PHASE-26 defines a post-GA operating review gate that binds live operations, release automation, field evidence, and lifecycle governance into an explicit next-stage decision surface.

## Exit criteria

- the PHASE-26 SSOT planning surfaces, work-items, acceptance, tests, and gates exist and validate
- unblocked PHASE-26 tasks are available through `python scripts/next_tasks.py`
- PHASE-25 remains closed while PHASE-26 is explicitly open

## What becomes unlocked after this phase

none yet
