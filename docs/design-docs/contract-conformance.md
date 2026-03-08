# Contract Conformance

## Purpose

PHASE-14 contract conformance exists to prove that the runtime-facing message layer
means the same thing across Elixir, Python, and Rust.

This is narrower than a full SDK.
It is also stricter than "the schemas happen to validate."

The conformance surface focuses on whether the control plane and execution plane
agree on:

- subject-to-message mapping
- lifecycle stage semantics
- required fields for dispatch, heartbeat, progress, cancel, and terminal callbacks
- the boundary between canonical runtime truth and worker-reported evidence

## Canonical sources

- `schema/proto/`
- `schema/transport-topology.yaml`
- `tests/conformance/fixtures/`

The transport topology remains the source of truth for subject routing.
Proto contracts remain the source of truth for runtime message shape.
Conformance fixtures exist to make those sources testable together.

## Initial conformance scope

The first conformance slice covers the runtime-worker lifecycle:

- worker registration
- worker heartbeat
- action dispatch
- action cancel
- action accepted
- action progress
- action heartbeat
- action completed
- action failed
- action cancelled

This is intentionally the minimum set required to keep control-plane and worker-plane
contracts coherent under replay, recovery, and transport changes.

## Rules

### Rule 1: topology and message names must agree

Every conformance fixture references a transport subject mapping that must resolve to
the same proto message name.

### Rule 2: lifecycle stages must stay explicit

Dispatch, progress, heartbeat, cancel, and terminal callbacks must keep distinct
semantics and may not collapse into a generic worker event.

### Rule 3: control plane truth stays authoritative

Conformance fixtures are allowed to prove worker payload shape and transport meaning.
They are not allowed to make the worker the owner of canonical session state.

### Rule 4: invalid fixtures must fail deterministically

Conformance assets are useful only if malformed subject bindings or message drift
cause a hard failure instead of a soft warning.

## What this unlocks

- replay diffing against a stable contract surface
- upgrade and skew validation
- stronger worker implementation confidence across languages
- a future extension certification baseline

## Non-goals

- full language SDK generation strategy
- marketplace review workflows
- connector certification policy
