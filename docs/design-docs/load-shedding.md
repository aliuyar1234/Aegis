# Load shedding

## Purpose

Load shedding in Aegis is a policy decision, not a vague incident response. PHASE-16
defines overload doctrine so the runtime preserves correctness and operator agency
under pressure.

## Doctrine

- operator-critical control flows must remain protected
- recovery work must remain protected
- already-approved effectful work must remain protected unless the policy explicitly
  denies new admission before dispatch
- lower-priority conveniences may be delayed or rejected with explicit reasons

## Response levels

- soft pressure: delay bounded low-priority work
- hard pressure: reject specific shed classes to preserve operator, recovery, and
  effectful paths

## Required evidence

Every overload response needs machine-readable evidence:

- triggering metric and threshold
- affected classes
- protected classes
- decision taken
- linked runbook

## Anti-patterns

- hidden degradation
- dropping operator or recovery events to save throughput
- conflating admission control with data-loss tolerance
