# Replay Oracle

## Purpose

This document defines the **replay oracle** for Aegis Runtime.
The oracle describes what counts as equivalent replay and which parts of session truth are:

- recomputable from canonical history
- reproducible only from captured evidence
- fundamentally unknowable without claiming false certainty

The replay oracle exists to keep replay, recovery, simulation, and upgrade work honest.

## Why this exists

Aegis already has replay.
What it needs at PHASE-14 is a stronger answer to a harder question:

**When should two replays be considered equivalent?**

Without that answer, replay can exist and still drift silently across:

- full replay from genesis
- hydrate-from-checkpoint plus tail replay
- historical operator replay
- later mixed-version upgrade rehearsal

## Determinism classes

The canonical catalog lives in `meta/determinism-classes.yaml`.

### 1. deterministic

These values are expected to be recomputed from canonical event history and runtime rules.

Examples:

- lifecycle state
- approval status transitions
- action ledger status transitions
- checkpoint selection rules
- projection fields derived only from canonical timeline data

### 2. captured-nondeterministic

These values are produced by external or time-sensitive systems, but Aegis can replay them by consuming recorded evidence rather than re-executing the world.

Examples:

- browser DOM snapshots
- screenshots and traces
- model/tool response payloads captured at runtime
- worker completion payloads
- externally produced identifiers recorded in canonical events or artifacts

Historical replay consumes captured evidence and **never re-dispatches the side effect** that created it.

### 3. externally-unknowable

These are facts about the external world that Aegis must not fabricate during replay.

Examples:

- the exact live external system state after an effectful action when no verification artifact was captured
- hidden server-side mutations outside the captured evidence boundary
- counterfactual state that was never observed by the runtime

For this class, replay may render uncertainty, evidence, and operator warnings.
It must not claim exact reconstruction.

## Replay modes

### Full replay

Rebuild session truth from genesis events only.

### Checkpoint-tail replay

Load the latest compatible checkpoint and replay the tail events after it.

### Historical replay

Render timeline, artifacts, approvals, and operator-visible state without any external re-execution.

## Equivalence surface

The canonical replay oracle lives in `meta/replay-equivalence.yaml`.
At minimum, replay equivalence is measured over:

- session lifecycle and mode
- approval ledger and waiting state
- action ledger and terminal action outcomes
- registered artifact metadata and evidence references
- uncertainty classification and quarantine state
- operator-visible timeline truth

## Explicit non-equivalence

Replay equivalence does **not** require byte-for-byte reproduction of fields whose purpose is observability rather than session truth, for example:

- transient tracing IDs
- process-local timing details
- storage-local insertion timing

Those fields may differ while the replay still counts as equivalent.

## Rules

### Rule 1: historical replay never re-executes side effects

Historical replay must never call model providers, browser workers, or external APIs.
It consumes canonical event payloads and artifact references only.

### Rule 2: checkpoint-tail replay must converge with full replay

For supported fixtures and compatible checkpoint versions, replay from checkpoint plus tail must yield equivalent current truth to replay from genesis.

### Rule 3: captured-nondeterministic evidence must be explicit

If a value depends on an external system but is expected to appear during replay, it must be captured in canonical payloads or artifact metadata.

### Rule 4: externally unknowable state is surfaced as uncertainty

When exact reconstruction is impossible, Aegis must preserve uncertainty and evidence, not pretend certainty.

## How the oracle is used

The replay oracle is meant to drive:

- replay phase gates
- deterministic simulation scenarios
- replay diff harnesses
- upgrade and restore drills
- benchmark scorecards

## Relationship to the event/replay model

`docs/design-docs/event-replay-model.md` defines the runtime event model and replay doctrine.
This document tightens the comparison contract used to decide whether replay remained correct across time and change.
