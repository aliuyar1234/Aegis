# Fleet triage product spec

## Purpose

Fleet triage is the PHASE-16 operator surface for reasoning about many sessions at
once. It complements session detail and replay. It does not replace them.

## Required outcomes

- compare cohorts of sessions rather than one session at a time
- identify repeated failure signatures
- link fleet observations back to explicit SLO, overload, placement, isolation, and
  storage evidence
- export an operator evidence bundle with bounded fields and runbook links

## Required cohort dimensions

- health state
- wait reason
- tenant tier
- selected pool versus expected pool
- pressure and isolation markers
- storage or projection lag markers

## Evidence bundle requirements

- no AI-generated summary standing in for evidence
- include cluster summaries, report verdicts, runbook links, and bounded evidence
  fields
- only reference recorded or policy-derived data

## Anti-patterns

- fleet views that summarize away the root cause
- unbounded full-session exports for convenience
- UI-only clustering detached from runtime evidence
