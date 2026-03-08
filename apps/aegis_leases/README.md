# aegis_leases

## Purpose

Single-owner lease semantics, fencing, and adoption

## Responsibilities

- PostgreSQL-backed lease persistence in `session_leases`
- authoritative renewal and epoch validation
- self-fencing and ambiguity handling
- adoption after expiry or node loss

## Must not own

- hidden authoritative state outside the assigned boundary
- logic that belongs to another app just because it is convenient

## First implementation note

When adding code here, link the module or boundary to the relevant phase doc, ADR, acceptance criteria, and tests.

## Phase 03 modules

- `Aegis.Leases` - public lease authority boundary
- `Aegis.Leases.SessionLease` - normalized lease row struct

## Validation

- `TS-005` - `python3 scripts/run_elixir_suite.py TS-005`
